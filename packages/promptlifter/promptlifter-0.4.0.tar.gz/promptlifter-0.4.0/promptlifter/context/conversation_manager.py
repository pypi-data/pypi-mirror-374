"""
Conversation Context Manager for maintaining chat history and context optimization.

This module handles conversation history, automatic summarization, and context
management for optimal LLM inference.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..config import MAX_CONTEXT_TOKENS, MAX_HISTORY_TOKENS
from ..nodes.llm_service import llm_service

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""

    user_message: str
    assistant_response: str
    timestamp: datetime
    tokens_used: int
    context_sources: List[
        str
    ]  # Sources of context used (e.g., "tavily", "pinecone", "history")


class ConversationContextManager:
    """
    Manages conversation history and context optimization for LLM interactions.

    Features:
    - Maintains conversation history with token counting
    - Automatic summarization of old interactions
    - Context relevance scoring
    - Configurable token limits
    """

    def __init__(
        self,
        max_history_tokens: int = MAX_HISTORY_TOKENS,
        max_context_tokens: int = MAX_CONTEXT_TOKENS,
    ):
        """
        Initialize the conversation context manager.

        Args:
            max_history_tokens: Maximum tokens to keep in conversation history
            max_context_tokens: Maximum tokens for context assembly
        """
        self.max_history_tokens = max_history_tokens
        self.max_context_tokens = max_context_tokens
        self.history: List[ConversationTurn] = []
        self.summary: Optional[str] = None
        self.current_tokens = 0

    def add_interaction(
        self,
        user_message: str,
        assistant_response: str,
        context_sources: Optional[List[str]] = None,
    ) -> None:
        """
        Add a new interaction to the conversation history.

        Args:
            user_message: User's input message
            assistant_response: Assistant's response
            context_sources: List of context sources used for this response
        """
        if context_sources is None:
            context_sources = []

        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        user_tokens = len(user_message) // 4
        assistant_tokens = len(assistant_response) // 4
        total_tokens = user_tokens + assistant_tokens

        turn = ConversationTurn(
            user_message=user_message,
            assistant_response=assistant_response,
            timestamp=datetime.now(),
            tokens_used=total_tokens,
            context_sources=context_sources,
        )

        self.history.append(turn)
        self.current_tokens += total_tokens

        logger.info(
            f"Added interaction: {total_tokens} tokens, total: {self.current_tokens}"
        )

        # Check if we need to summarize old history
        if self.current_tokens > self.max_history_tokens:
            asyncio.create_task(self._summarize_old_history())

    def add_turn(self, turn: ConversationTurn) -> None:
        """
        Add a conversation turn to the history.

        Args:
            turn: ConversationTurn object to add
        """
        self.history.append(turn)
        self.current_tokens += turn.tokens_used

        logger.info(
            f"Added turn: {turn.tokens_used} tokens, total: {self.current_tokens}"
        )

        # Check if we need to summarize old history
        if self.current_tokens > self.max_history_tokens:
            asyncio.create_task(self._summarize_old_history())

    async def get_optimized_context(self, current_query: str) -> str:
        """
        Get optimized context for the current query.

        Args:
            current_query: The current user query

        Returns:
            Optimized context string for LLM inference
        """
        context_parts = []
        current_tokens = 0

        # Add conversation summary if available
        if self.summary:
            summary_tokens = len(self.summary) // 4
            if current_tokens + summary_tokens <= self.max_context_tokens:
                context_parts.append(f"Conversation Summary: {self.summary}")
                current_tokens += summary_tokens

        # Add recent conversation history (most recent first)
        for turn in reversed(self.history[-5:]):  # Last 5 turns
            turn_context = (
                f"User: {turn.user_message}\nAssistant: {turn.assistant_response}"
            )
            turn_tokens = len(turn_context) // 4

            if current_tokens + turn_tokens <= self.max_context_tokens:
                context_parts.append(turn_context)
                current_tokens += turn_tokens
            else:
                break

        # Reverse to get chronological order
        context_parts.reverse()

        if context_parts:
            return "\n\n".join(context_parts)
        return ""

    async def _summarize_old_history(self) -> None:
        """Summarize old conversation history to maintain token limits."""
        if len(self.history) < 3:  # Don't summarize if too few interactions
            return

        try:
            # Take first 70% of history for summarization
            summarize_count = int(len(self.history) * 0.7)
            turns_to_summarize = self.history[:summarize_count]

            # Create summary prompt
            conversation_text = "\n\n".join(
                [
                    f"User: {turn.user_message}\nAssistant: {turn.assistant_response}"
                    for turn in turns_to_summarize
                ]
            )

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Summarize this conversation history in 2-3 sentences. "
                        "Focus on key topics, decisions, and context that would be "
                        "useful for future interactions. Be concise but preserve "
                        "important details."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Conversation to summarize:\n\n{conversation_text}",
                },
            ]

            summary_response = await llm_service.generate(messages, max_tokens=200)
            self.summary = summary_response.strip()

            # Remove summarized turns from history
            self.history = self.history[summarize_count:]

            # Recalculate current tokens
            self.current_tokens = sum(turn.tokens_used for turn in self.history)

            logger.info(
                f"Summarized {summarize_count} turns, new token count: "
                f"{self.current_tokens}"
            )

        except Exception as e:
            logger.error(f"Failed to summarize conversation history: {e}")
            # Fallback: just remove oldest turns
            self.history = self.history[-10:]  # Keep last 10 turns
            self.current_tokens = sum(turn.tokens_used for turn in self.history)

    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about the current conversation."""
        return {
            "total_turns": len(self.history),
            "current_tokens": self.current_tokens,
            "max_history_tokens": self.max_history_tokens,
            "has_summary": self.summary is not None,
            "context_sources_used": list(
                set(
                    [source for turn in self.history for source in turn.context_sources]
                )
            ),
        }

    def clear_history(self) -> None:
        """Clear all conversation history and summary."""
        self.history.clear()
        self.summary = None
        self.current_tokens = 0
        logger.info("Conversation history cleared")

    def export_history(self) -> List[Dict[str, Any]]:
        """Export conversation history for persistence."""
        return [
            {
                "user_message": turn.user_message,
                "assistant_response": turn.assistant_response,
                "timestamp": turn.timestamp.isoformat(),
                "tokens_used": turn.tokens_used,
                "context_sources": turn.context_sources,
            }
            for turn in self.history
        ]

    def import_history(self, history_data: List[Dict[str, Any]]) -> None:
        """Import conversation history from persistence."""
        self.clear_history()

        for turn_data in history_data:
            turn = ConversationTurn(
                user_message=turn_data["user_message"],
                assistant_response=turn_data["assistant_response"],
                timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                tokens_used=turn_data["tokens_used"],
                context_sources=turn_data.get("context_sources", []),
            )
            self.history.append(turn)
            self.current_tokens += turn.tokens_used

        logger.info(f"Imported {len(history_data)} conversation turns")

    def update_config(
        self,
        max_history_tokens: Optional[int] = None,
        max_context_tokens: Optional[int] = None,
    ) -> None:
        """
        Update configuration parameters.

        Args:
            max_history_tokens: New maximum history tokens
            max_context_tokens: New maximum context tokens
        """
        if max_history_tokens is not None:
            self.max_history_tokens = max_history_tokens
            logger.info(f"Updated max_history_tokens to {max_history_tokens}")

        if max_context_tokens is not None:
            self.max_context_tokens = max_context_tokens
            logger.info(f"Updated max_context_tokens to {max_context_tokens}")
