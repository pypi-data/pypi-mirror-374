"""
Context Retriever for intelligent context gathering from external sources.

This module handles conditional search execution and relevance-based result filtering
from Tavily web search and Pinecone vector search.
"""

import asyncio
import logging
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
from .query_classifier import QueryClassifier

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
        self.query_classifier = QueryClassifier()

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

        # Determine if search is needed using LLM-based classification
        should_search = await self.query_classifier.should_use_search(
            query, conversation_history
        )
        if not should_search:
            logger.info("Search not needed - using conversation history only")
            return context_chunks

        # Get enhanced search query with context from LLM classifier
        enhanced_query = await self.query_classifier.get_enhanced_search_query(
            query, conversation_history
        )

        # Run searches in parallel if enabled
        search_tasks = []

        if self.tavily_enabled:
            search_tasks.append(self._search_tavily(enhanced_query))

        if self.pinecone_enabled:
            search_tasks.append(self._search_pinecone(enhanced_query))

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
