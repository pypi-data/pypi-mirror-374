"""
ConversationLLM - Simplified conversation-focused LLM interface.

This module provides a streamlined interface for conversational LLM interactions
with intelligent context management and optional search integration.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .config import (
    ENABLE_AUTO_SEARCH,
    MAX_CONTEXT_TOKENS,
    MAX_HISTORY_TOKENS,
    SEARCH_RELEVANCE_THRESHOLD,
)
from .context import ContextOptimizer, ContextRetriever, ConversationContextManager
from .nodes.llm_service import llm_service

logger = logging.getLogger(__name__)


@dataclass
class ConversationConfig:
    """Configuration for ConversationLLM."""

    max_history_tokens: int = MAX_HISTORY_TOKENS
    max_context_tokens: int = MAX_CONTEXT_TOKENS
    enable_auto_search: bool = ENABLE_AUTO_SEARCH
    search_relevance_threshold: float = SEARCH_RELEVANCE_THRESHOLD
    system_prompt: str = (
        "You are a helpful AI assistant. Provide clear, accurate, and helpful "
        "responses based on the conversation context and any relevant information "
        "provided. Be conversational and engaging while maintaining accuracy."
    )


@dataclass
class ConversationResponse:
    """Response from a conversation interaction."""

    message: str
    context_sources: List[str]
    tokens_used: int
    conversation_stats: Dict[str, Any]


class ConversationLLM:
    """
    Simplified conversation-focused LLM interface.

    Features:
    - Automatic context management with conversation history
    - Optional search integration (Tavily, Pinecone)
    - Intelligent context optimization
    - Simple chat interface
    """

    def __init__(self, config: Optional[ConversationConfig] = None):
        """
        Initialize the ConversationLLM.

        Args:
            config: Configuration for the conversation LLM
        """
        self.config = config or ConversationConfig()

        # Initialize components
        self.context_manager = ConversationContextManager(
            max_history_tokens=self.config.max_history_tokens,
            max_context_tokens=self.config.max_context_tokens,
        )

        self.context_retriever = ContextRetriever(
            enable_auto_search=self.config.enable_auto_search,
            relevance_threshold=self.config.search_relevance_threshold,
        )

        self.context_optimizer = ContextOptimizer(
            max_tokens=self.config.max_context_tokens,
            relevance_threshold=self.config.search_relevance_threshold,
        )

        logger.info(
            f"ConversationLLM initialized with config: "
            f"max_history={self.config.max_history_tokens}, "
            f"max_context={self.config.max_context_tokens}, "
            f"auto_search={self.config.enable_auto_search}"
        )

    async def chat(self, message: str) -> ConversationResponse:
        """
        Chat with the LLM using conversation context.

        Args:
            message: User message

        Returns:
            ConversationResponse with the assistant's response and metadata
        """
        try:
            logger.info(f"Processing chat message: {message[:50]}...")

            # Get conversation history context
            conversation_history = await self.context_manager.get_optimized_context(
                message
            )

            # Retrieve relevant context from external sources
            retrieved_context = await self.context_retriever.retrieve_relevant_context(
                message, conversation_history
            )

            # Optimize context for LLM inference
            optimized_context = self.context_optimizer.optimize_context(
                conversation_history, retrieved_context, message
            )

            # Prepare messages for LLM
            messages = self._prepare_messages(message, optimized_context.content)

            # Generate response
            response = await llm_service.generate(messages, max_tokens=1000)

            # Extract context sources used
            context_sources = optimized_context.sources_used.copy()

            # Add interaction to conversation history
            self.context_manager.add_interaction(message, response, context_sources)

            # Calculate tokens used
            tokens_used = self._estimate_tokens(message + response)

            # Get conversation statistics
            conversation_stats = self.context_manager.get_conversation_stats()

            logger.info(
                f"Chat completed - tokens: {tokens_used}, "
                f"sources: {context_sources}"
            )

            return ConversationResponse(
                message=response,
                context_sources=context_sources,
                tokens_used=tokens_used,
                conversation_stats=conversation_stats,
            )

        except Exception as e:
            logger.error(f"Chat failed: {e}")
            error_response = f"I apologize, but I encountered an error: {str(e)}"

            return ConversationResponse(
                message=error_response,
                context_sources=[],
                tokens_used=self._estimate_tokens(error_response),
                conversation_stats=self.context_manager.get_conversation_stats(),
            )

    def _prepare_messages(
        self, user_message: str, context: str
    ) -> List[Dict[str, str]]:
        """
        Prepare messages for LLM inference.

        Args:
            user_message: User's message
            context: Optimized context

        Returns:
            List of messages for LLM
        """
        messages = [{"role": "system", "content": self.config.system_prompt}]

        # Add context if available
        if context:
            messages.append({"role": "system", "content": f"Context:\n{context}"})

        # Add user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        if not text:
            return 0
        return len(text) // 4  # Rough estimation

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.context_manager.clear_history()
        logger.info("Conversation cleared")

    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        return self.context_manager.get_conversation_stats()

    def export_conversation(self) -> List[Dict[str, Any]]:
        """Export conversation history."""
        return self.context_manager.export_history()

    def import_conversation(self, history: List[Dict[str, Any]]) -> None:
        """Import conversation history."""
        self.context_manager.import_history(history)

    def update_config(self, **kwargs: Any) -> None:
        """
        Update configuration parameters.

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated config: {key} = {value}")
            else:
                logger.warning(f"Unknown config parameter: {key}")

        # Update context manager configuration
        if "max_history_tokens" in kwargs:
            self.context_manager.update_config(
                max_history_tokens=kwargs["max_history_tokens"]
            )
        if "max_context_tokens" in kwargs:
            self.context_manager.update_config(
                max_context_tokens=kwargs["max_context_tokens"]
            )

        # Update context retriever configuration
        if "enable_auto_search" in kwargs:
            self.context_retriever.enable_auto_search = kwargs["enable_auto_search"]
        if "search_relevance_threshold" in kwargs:
            self.context_retriever.relevance_threshold = kwargs[
                "search_relevance_threshold"
            ]

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            "max_history_tokens": self.config.max_history_tokens,
            "max_context_tokens": self.config.max_context_tokens,
            "enable_auto_search": self.config.enable_auto_search,
            "search_relevance_threshold": self.config.search_relevance_threshold,
            "system_prompt": self.config.system_prompt,
        }

    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get context retrieval statistics."""
        return self.context_retriever.get_retrieval_stats()

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get context optimization statistics."""
        return self.context_optimizer.get_optimization_stats()


# Convenience function for quick usage
async def quick_chat(
    message: str,
    max_history_tokens: int = MAX_HISTORY_TOKENS,
    enable_search: bool = ENABLE_AUTO_SEARCH,
) -> str:
    """
    Quick chat function for simple usage.

    Args:
        message: User message
        max_history_tokens: Maximum tokens for conversation history
        enable_search: Whether to enable automatic search

    Returns:
        Assistant response
    """
    config = ConversationConfig(
        max_history_tokens=max_history_tokens, enable_auto_search=enable_search
    )

    llm = ConversationLLM(config)
    response = await llm.chat(message)
    return response.message
