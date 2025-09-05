"""
Context Optimizer for intelligent context assembly and optimization.

This module handles token-aware context assembly, relevance scoring, and
context compression for optimal LLM inference.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .context_retriever import ContextChunk

logger = logging.getLogger(__name__)


@dataclass
class OptimizedContext:
    """Represents optimized context for LLM inference."""

    content: str
    total_tokens: int
    sources_used: List[str]
    compression_ratio: float
    relevance_scores: Dict[str, float]


class ContextOptimizer:
    """
    Optimizes and combines context for LLM inference.

    Features:
    - Token-aware context assembly
    - Relevance scoring and filtering
    - Context compression techniques
    - Priority-based context selection
    """

    def __init__(
        self,
        max_tokens: int = 6000,
        relevance_threshold: float = 0.7,
        enable_compression: bool = True,
    ):
        """
        Initialize the context optimizer.

        Args:
            max_tokens: Maximum total tokens for context
            relevance_threshold: Minimum relevance score for including content
            enable_compression: Whether to use compression techniques
        """
        self.max_tokens = max_tokens
        self.relevance_threshold = relevance_threshold
        self.enable_compression = enable_compression

        logger.info(
            f"ContextOptimizer initialized - max_tokens: {max_tokens}, "
            f"relevance_threshold: {relevance_threshold}, "
            f"compression: {enable_compression}"
        )

    def optimize_context(
        self,
        conversation_history: str,
        retrieved_context: Union[str, List[ContextChunk]],
        current_query: str,
    ) -> OptimizedContext:
        """
        Optimize and combine context for LLM inference.

        Args:
            conversation_history: Existing conversation context
            retrieved_context: Retrieved context chunks from search
            current_query: Current user query

        Returns:
            Optimized context for LLM inference
        """
        logger.info(
            f"Optimizing context - history: {len(conversation_history)} chars, "
            f"retrieved: {len(retrieved_context)} chunks"
        )

        # Start with conversation history
        context_parts = []
        total_tokens = 0
        sources_used = []
        relevance_scores = {}

        # Add conversation history if available
        if conversation_history:
            history_tokens = self._estimate_tokens(conversation_history)
            if history_tokens <= self.max_tokens * 0.6:  # Reserve 60% for history
                context_parts.append(f"Conversation History:\n{conversation_history}")
                total_tokens += history_tokens
                sources_used.append("conversation_history")
                relevance_scores["conversation_history"] = 1.0

        # Add retrieved context chunks
        remaining_tokens = self.max_tokens - total_tokens

        # Ensure retrieved_context is a list of ContextChunk objects
        if isinstance(retrieved_context, str):
            # Convert string to ContextChunk
            context_chunks = [
                ContextChunk(
                    content=retrieved_context,
                    source="retrieved",
                    metadata={"query": current_query},
                )
            ]
        else:
            # Must be List[ContextChunk] based on Union type
            context_chunks = retrieved_context

        added_chunks = self._select_best_chunks(
            context_chunks, remaining_tokens, current_query
        )

        for chunk in added_chunks:
            chunk_tokens = self._estimate_tokens(chunk.content)
            if total_tokens + chunk_tokens <= self.max_tokens:
                # Format chunk with source information
                formatted_chunk = self._format_context_chunk(chunk)
                context_parts.append(formatted_chunk)
                total_tokens += chunk_tokens
                sources_used.append(chunk.source)
                relevance_scores[chunk.source] = 0.8  # Default relevance score

        # Combine all context parts
        final_context = "\n\n".join(context_parts)

        # Apply compression if enabled and needed
        if self.enable_compression and total_tokens > self.max_tokens * 0.9:
            final_context, compression_ratio = self._compress_context(
                final_context, self.max_tokens
            )
        else:
            compression_ratio = 1.0

        # Recalculate tokens after compression
        final_tokens = self._estimate_tokens(final_context)

        logger.info(
            f"Context optimization complete - final tokens: {final_tokens}, "
            f"sources: {sources_used}, compression: {compression_ratio:.2f}"
        )

        return OptimizedContext(
            content=final_context,
            total_tokens=final_tokens,
            sources_used=sources_used,
            compression_ratio=compression_ratio,
            relevance_scores=relevance_scores,
        )

    def _select_best_chunks(
        self, chunks: List[ContextChunk], max_tokens: int, query: str
    ) -> List[ContextChunk]:
        """
        Select the best context chunks within token limits.

        Args:
            chunks: Available context chunks
            max_tokens: Maximum tokens available
            query: Current query for relevance scoring

        Returns:
            Selected chunks in priority order
        """
        if not chunks:
            return []

        # Select chunks within token limit (no relevance scoring)
        selected_chunks = []
        current_tokens = 0

        for chunk in chunks:
            chunk_tokens = self._estimate_tokens(chunk.content)
            if current_tokens + chunk_tokens <= max_tokens:
                selected_chunks.append(chunk)
                current_tokens += chunk_tokens
            else:
                # Try to fit a compressed version
                compressed_content = self._compress_text(
                    chunk.content, max_tokens - current_tokens
                )
                if compressed_content:
                    compressed_chunk = ContextChunk(
                        content=compressed_content,
                        source=chunk.source,
                        metadata=chunk.metadata,
                    )
                    selected_chunks.append(compressed_chunk)
                    break

        return selected_chunks

    def _format_context_chunk(self, chunk: ContextChunk) -> str:
        """Format a context chunk with source information."""
        source_label = {
            "tavily": "Web Search Results",
            "pinecone": "Knowledge Base Results",
            "history": "Conversation History",
        }.get(chunk.source, f"{chunk.source.title()} Results")

        return f"{source_label}:\n{chunk.content}"

    def _compress_context(self, context: str, max_tokens: int) -> tuple[str, float]:
        """
        Compress context to fit within token limits.

        Args:
            context: Context to compress
            max_tokens: Maximum tokens allowed

        Returns:
            Tuple of (compressed_context, compression_ratio)
        """
        original_tokens = self._estimate_tokens(context)
        if original_tokens <= max_tokens:
            return context, 1.0

        # Apply compression techniques
        compressed = context

        # 1. Remove excessive whitespace
        compressed = re.sub(r"\n\s*\n\s*\n", "\n\n", compressed)

        # 2. Truncate long sentences
        sentences = compressed.split(". ")
        if len(sentences) > 10:
            # Keep first 5 and last 5 sentences
            compressed = ". ".join(sentences[:5] + ["..."] + sentences[-5:])

        # 3. Remove redundant phrases
        redundant_patterns = [
            r"\b(please note that|it is important to note that|"
            r"it should be noted that)\b",
            r"\b(in other words|that is to say|in summary)\b",
            r"\b(as mentioned earlier|as stated previously|as discussed above)\b",
        ]

        for pattern in redundant_patterns:
            compressed = re.sub(pattern, "", compressed, flags=re.IGNORECASE)

        # 4. If still too long, truncate by paragraphs
        if self._estimate_tokens(compressed) > max_tokens:
            paragraphs = compressed.split("\n\n")
            if len(paragraphs) > 3:
                # Keep first 2 and last 1 paragraphs
                compressed = "\n\n".join(paragraphs[:2] + ["..."] + paragraphs[-1:])

        # 5. Final truncation if necessary
        if self._estimate_tokens(compressed) > max_tokens:
            # Truncate to fit
            target_chars = int(max_tokens * 4)  # Rough estimate: 1 token = 4 chars
            compressed = compressed[:target_chars] + "..."

        final_tokens = self._estimate_tokens(compressed)
        compression_ratio = (
            final_tokens / original_tokens if original_tokens > 0 else 1.0
        )

        logger.info(
            f"Context compressed: {original_tokens} -> {final_tokens} tokens "
            f"(ratio: {compression_ratio:.2f})"
        )

        return compressed, compression_ratio

    def _compress_text(self, text: str, max_tokens: int) -> Optional[str]:
        """Compress a single text to fit within token limit."""
        if self._estimate_tokens(text) <= max_tokens:
            return text

        # Simple truncation with ellipsis
        target_chars = int(max_tokens * 4)
        if target_chars < 100:  # Too small to be useful
            return None

        return text[:target_chars] + "..."

    def _score_relevance_to_query(self, content: str, query: str) -> float:
        """
        Score relevance of content to query.

        Args:
            content: Content to score
            query: Query to match against

        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not content or not query:
            return 0.0

        content_lower = content.lower()
        query_lower = query.lower()

        # Extract key terms from query
        query_words = set(re.findall(r"\b\w+\b", query_lower))
        content_words = set(re.findall(r"\b\w+\b", content_lower))

        # Remove common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
        }
        query_words = query_words - stop_words
        content_words = content_words - stop_words

        if not query_words:
            return 0.0

        # Calculate word overlap
        common_words = query_words.intersection(content_words)
        word_overlap_score = len(common_words) / len(query_words)

        # Boost for exact phrase matches
        phrase_boost = 0.0
        if query_lower in content_lower:
            phrase_boost = 0.3

        # Boost for question word matches
        question_words = {"what", "how", "when", "where", "why", "who", "which"}
        question_boost = 0.0
        for word in question_words:
            if word in query_lower and word in content_lower:
                question_boost += 0.1

        # Combine scores
        total_score = min(1.0, word_overlap_score + phrase_boost + question_boost)

        return total_score

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        # Rough estimation: 1 token ≈ 4 characters for English text
        # This is a simplified approach; real tokenization would be more accurate
        return len(text) // 4

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get statistics about the context optimizer."""
        return {
            "max_tokens": self.max_tokens,
            "relevance_threshold": self.relevance_threshold,
            "compression_enabled": self.enable_compression,
            "token_estimation_method": "character_based_approximation",
        }
