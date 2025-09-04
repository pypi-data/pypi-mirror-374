"""
Context Retriever for intelligent context gathering from external sources.

This module handles conditional search execution and relevance-based result filtering
from Tavily web search and Pinecone vector search.
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..config import (
    ENABLE_AUTO_SEARCH,
    PINECONE_API_KEY,
    SEARCH_RELEVANCE_THRESHOLD,
    TAVILY_API_KEY,
)
from ..nodes.run_pinecone_search import run_pinecone_search
from ..nodes.run_tavily_search import run_tavily_search

logger = logging.getLogger(__name__)


@dataclass
class ContextChunk:
    """Represents a chunk of retrieved context."""

    content: str
    source: str  # "tavily", "pinecone", "history"
    metadata: Optional[Dict[str, Any]] = None


class ContextRetriever:
    """
    Intelligent context retriever that conditionally uses search sources.

    Features:
    - Conditional search execution based on query type and existing context
    - Relevance-based result filtering
    - Support for both Tavily and Pinecone (optional)
    - Query type detection (conversational vs research)
    """

    def __init__(
        self,
        enable_auto_search: bool = ENABLE_AUTO_SEARCH,
        relevance_threshold: float = SEARCH_RELEVANCE_THRESHOLD,
    ):
        """
        Initialize the context retriever.

        Args:
            enable_auto_search: Whether to automatically use search when needed
            relevance_threshold: Minimum relevance score for including results
        """
        self.enable_auto_search = enable_auto_search
        self.relevance_threshold = relevance_threshold
        self.tavily_enabled = bool(TAVILY_API_KEY)
        self.pinecone_enabled = bool(PINECONE_API_KEY)

        logger.info(
            f"ContextRetriever initialized - Tavily: {self.tavily_enabled}, "
            f"Pinecone: {self.pinecone_enabled}, Auto-search: {enable_auto_search}"
        )

    async def retrieve_relevant_context(
        self, query: str, conversation_history: str = ""
    ) -> List[ContextChunk]:
        """
        Retrieve relevant context from available sources.

        Args:
            query: Current user query
            conversation_history: Existing conversation context

        Returns:
            List of relevant context chunks
        """
        context_chunks: List[ContextChunk] = []

        # Determine if search is needed
        if not self.should_use_search(query, conversation_history):
            logger.info("Search not needed - using conversation history only")
            return context_chunks

        # Run searches in parallel if enabled
        search_tasks = []

        if self.tavily_enabled:
            search_tasks.append(self._search_tavily(query))

        if self.pinecone_enabled:
            search_tasks.append(self._search_pinecone(query))

        if search_tasks:
            logger.info(f"Running {len(search_tasks)} search operations in parallel")
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

            # Process search results
            for i, result in enumerate(search_results):
                if isinstance(result, Exception):
                    logger.error(f"Search {i} failed: {result}")
                    continue

                if isinstance(result, ContextChunk):
                    context_chunks.append(result)

        # Use all retrieved chunks - trust search results are relevant
        logger.info(f"Retrieved {len(context_chunks)} context chunks")

        return context_chunks

    def should_use_search(self, query: str, history: str) -> bool:
        """
        Determine if search is needed based on query type and existing context.

        Args:
            query: Current user query
            history: Existing conversation history

        Returns:
            True if search should be used
        """
        if not self.enable_auto_search:
            return False

        # Check if we have search capabilities
        if not (self.tavily_enabled or self.pinecone_enabled):
            return False

        query_lower = query.lower()

        # Check for conversational patterns that typically don't need search FIRST
        conversational_patterns = [
            r"\b(how are you|how do you do|hello|hi|hey)\b",
            r"\b(thank you|thanks|goodbye|bye)\b",
            r"\b(yes|no|ok|okay|sure|alright)\b",
            r"\b(please|can you|could you|would you)\b.*\b(help|assist|do)\b",
        ]

        for pattern in conversational_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.info("Search not needed - conversational query")
                return False

        # If we have substantial conversation history, be more conservative about search
        has_substantial_history = history and len(history.split()) > 50

        # Check for follow-up patterns that should use conversation context
        follow_up_patterns = [
            r"\b(can you give me an example|give me an example|show me an example)\b",
            r"\b(what about|how about|tell me more|more details|elaborate)\b",
            r"\b(what else|anything else|other examples|other cases)\b",
            r"\b(how does that work|how is that done|how do you do that)\b",
            r"\b(what do you mean|can you explain|clarify)\b",
        ]

        for pattern in follow_up_patterns:
            if (
                re.search(pattern, query_lower, re.IGNORECASE)
                and has_substantial_history
            ):
                logger.info(
                    "Search not needed - follow-up question with sufficient context"
                )
                return False

        # Detect query types that typically need search (but only if not a follow-up)
        search_indicators = [
            r"\b(latest|recent|current|new|today|yesterday|this week|this month)\b",
            r"\b(compare|difference between|vs|versus)\b",
            r"\b(statistics|data|research|study|report)\b",
            r"\b(price|cost|costs|pricing)\b",
            r"\b(weather|forecast|temperature)\b",
            r"\b(news|update|breaking|announcement)\b",
        ]

        # Check for search indicators
        for pattern in search_indicators:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.info(f"Search needed - detected pattern: {pattern}")
                return True

        # For general questions, only search if we don't have much context
        general_question_patterns = [
            r"\b(what|how|when|where|why|who)\b.*\b"
            r"(is|are|was|were|will|can|could|should|would)\b",
            r"\b(explain|describe|tell me about|information about)\b",
        ]

        for pattern in general_question_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                if not has_substantial_history:
                    logger.info(
                        f"Search needed - general question with limited context: "
                        f"{pattern}"
                    )
                    return True
                else:
                    logger.info(
                        f"Search not needed - sufficient context: " f"{pattern}"
                    )
                    return False

        # Check if query is very short (likely needs context)
        if len(query.split()) < 3:
            logger.info("Search needed - very short query")
            return True

        # Check if conversation history is empty or very short
        if not history or len(history.split()) < 10:
            logger.info("Search needed - limited conversation history")
            return True

        logger.info("Search not needed - sufficient context available")
        return False

    async def _search_tavily(self, query: str) -> Optional[ContextChunk]:
        """Search using Tavily web search."""
        try:
            logger.info(f"Running Tavily search for: {query[:50]}...")
            result = await run_tavily_search(query)

            if (
                result
                and not result.startswith("[Error:")
                and not result.startswith("[Info:")
            ):
                return ContextChunk(
                    content=result,
                    source="tavily",
                    metadata={"query": query, "search_type": "web"},
                )

            logger.warning(f"Tavily search returned no useful results: {result[:100]}")
            return None

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return None

    async def _search_pinecone(self, query: str) -> Optional[ContextChunk]:
        """Search using Pinecone vector search."""
        try:
            logger.info(f"Running Pinecone search for: {query[:50]}...")
            result = await run_pinecone_search(query)

            if (
                result
                and not result.startswith("[Error:")
                and not result.startswith("[Info:")
            ):
                return ContextChunk(
                    content=result,
                    source="pinecone",
                    metadata={"query": query, "search_type": "vector"},
                )

            logger.warning(
                f"Pinecone search returned no useful results: {result[:100]}"
            )
            return None

        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return None

    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about the context retriever."""
        return {
            "tavily_enabled": self.tavily_enabled,
            "pinecone_enabled": self.pinecone_enabled,
            "auto_search_enabled": self.enable_auto_search,
            "relevance_threshold": self.relevance_threshold,
            "search_capabilities": {
                "web_search": self.tavily_enabled,
                "vector_search": self.pinecone_enabled,
                "both_enabled": self.tavily_enabled and self.pinecone_enabled,
            },
        }
