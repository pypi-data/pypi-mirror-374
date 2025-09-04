"""
Simplified unit tests for conversation interface components.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from promptlifter.context.context_optimizer import ContextOptimizer, OptimizedContext
from promptlifter.context.context_retriever import ContextChunk, ContextRetriever
from promptlifter.context.conversation_manager import (
    ConversationContextManager,
    ConversationTurn,
)
from promptlifter.conversation_llm import (
    ConversationConfig,
    ConversationLLM,
    quick_chat,
)


class TestConversationTurn:
    """Test ConversationTurn class."""

    def test_conversation_turn_creation(self) -> None:
        """Test ConversationTurn creation."""
        from datetime import datetime

        turn = ConversationTurn(
            user_message="Hello, how are you?",
            assistant_response="I'm doing well, thank you!",
            timestamp=datetime.now(),
            tokens_used=10,
            context_sources=["history"],
        )

        assert turn.user_message == "Hello, how are you?"
        assert turn.assistant_response == "I'm doing well, thank you!"
        assert isinstance(turn.timestamp, datetime)
        assert turn.tokens_used == 10
        assert turn.context_sources == ["history"]


class TestConversationContextManager:
    """Test ConversationContextManager class."""

    def test_conversation_context_manager_initialization(self) -> None:
        """Test ConversationContextManager initialization."""
        manager = ConversationContextManager()

        assert manager.max_history_tokens == 4000  # Default value
        assert len(manager.history) == 0
        assert manager.current_tokens == 0
        assert manager.summary is None

    def test_add_interaction(self) -> None:
        """Test adding interactions to conversation."""
        manager = ConversationContextManager()

        manager.add_interaction("Hello", "Hi there!", ["history"])

        assert len(manager.history) == 1
        assert manager.current_tokens > 0
        assert manager.history[0].user_message == "Hello"
        assert manager.history[0].assistant_response == "Hi there!"

    def test_clear_history(self) -> None:
        """Test clearing conversation history."""
        manager = ConversationContextManager()

        # Add some interactions
        manager.add_interaction("Hello", "Hi there!", ["history"])
        manager.add_interaction("How are you?", "I'm doing well!", ["history"])

        assert len(manager.history) == 2
        assert manager.current_tokens > 0

        manager.clear_history()

        assert len(manager.history) == 0
        assert manager.current_tokens == 0

    def test_export_history(self) -> None:
        """Test exporting conversation history."""
        manager = ConversationContextManager()

        # Add some interactions
        manager.add_interaction("Hello", "Hi there!", ["history"])
        manager.add_interaction("How are you?", "I'm doing well!", ["history"])

        exported = manager.export_history()

        assert len(exported) == 2
        assert exported[0]["user_message"] == "Hello"
        assert exported[0]["assistant_response"] == "Hi there!"
        assert exported[1]["user_message"] == "How are you?"
        assert exported[1]["assistant_response"] == "I'm doing well!"

    def test_import_history(self) -> None:
        """Test importing conversation history."""
        from datetime import datetime

        manager = ConversationContextManager()

        history = [
            {
                "user_message": "Hello",
                "assistant_response": "Hi there!",
                "timestamp": datetime.now().isoformat(),
                "tokens_used": 5,
                "context_sources": ["history"],
            },
            {
                "user_message": "How are you?",
                "assistant_response": "I'm doing well!",
                "timestamp": datetime.now().isoformat(),
                "tokens_used": 8,
                "context_sources": ["history"],
            },
        ]

        manager.import_history(history)

        assert len(manager.history) == 2
        assert manager.current_tokens == 13
        assert manager.history[0].user_message == "Hello"
        assert manager.history[1].user_message == "How are you?"


class TestContextChunk:
    """Test ContextChunk class."""

    def test_context_chunk_creation(self) -> None:
        """Test ContextChunk creation."""
        chunk = ContextChunk(
            content="This is test content", source="tavily", metadata={"tokens": 10}
        )

        assert chunk.content == "This is test content"
        assert chunk.source == "tavily"
        assert chunk.metadata == {"tokens": 10}


class TestContextRetriever:
    """Test ContextRetriever class."""

    def test_context_retriever_initialization(self) -> None:
        """Test ContextRetriever initialization."""
        retriever = ContextRetriever()

        assert retriever.enable_auto_search is True
        assert retriever.relevance_threshold == 0.7
        assert retriever.tavily_enabled is True
        assert retriever.pinecone_enabled is True

    def test_should_use_search(self) -> None:
        """Test search decision logic."""
        retriever = ContextRetriever()

        # Research queries should use search
        assert retriever.should_use_search("What is machine learning?", "") is True
        assert retriever.should_use_search("Research quantum computing", "") is True
        assert retriever.should_use_search("Tell me about AI", "") is True

        # Conversational queries should not trigger search
        assert (
            retriever.should_use_search("How are you?", "") is False
        )  # Conversational pattern
        assert (
            retriever.should_use_search("Hello", "") is False
        )  # Conversational pattern
        assert (
            retriever.should_use_search("Thanks", "") is False
        )  # Conversational pattern

        # With sufficient conversation history, some queries might not need search
        long_history = "This is a long conversation history " * 20  # ~500 words
        assert (
            retriever.should_use_search(
                "That's very helpful, thank you for the detailed explanation",
                long_history,
            )
            is False
        )


class TestOptimizedContext:
    """Test OptimizedContext class."""

    def test_optimized_context_creation(self) -> None:
        """Test OptimizedContext creation."""
        context = OptimizedContext(
            content="Optimized context content",
            total_tokens=100,
            sources_used=["tavily", "pinecone"],
            compression_ratio=0.8,
            relevance_scores={"tavily": 0.9, "pinecone": 0.7},
        )

        assert context.content == "Optimized context content"
        assert context.sources_used == ["tavily", "pinecone"]
        assert context.total_tokens == 100
        assert context.compression_ratio == 0.8
        assert context.relevance_scores == {"tavily": 0.9, "pinecone": 0.7}


class TestContextOptimizer:
    """Test ContextOptimizer class."""

    def test_context_optimizer_initialization(self) -> None:
        """Test ContextOptimizer initialization."""
        optimizer = ContextOptimizer()

        assert optimizer.max_tokens == 6000  # Default value from config
        assert optimizer.relevance_threshold == 0.7
        assert optimizer.enable_compression is True


class TestConversationConfig:
    """Test ConversationConfig class."""

    def test_conversation_config_defaults(self) -> None:
        """Test ConversationConfig with default values."""
        config = ConversationConfig()

        assert config.max_history_tokens == 4000
        assert config.max_context_tokens == 2000
        assert config.enable_auto_search is True
        assert config.search_relevance_threshold == 0.7
        assert "helpful" in config.system_prompt.lower()

    def test_conversation_config_custom(self) -> None:
        """Test ConversationConfig with custom values."""
        config = ConversationConfig(
            max_history_tokens=3000,
            max_context_tokens=1500,
            enable_auto_search=False,
            search_relevance_threshold=0.8,
            system_prompt="You are a coding assistant.",
        )

        assert config.max_history_tokens == 3000
        assert config.max_context_tokens == 1500
        assert config.enable_auto_search is False
        assert config.search_relevance_threshold == 0.8
        assert config.system_prompt == "You are a coding assistant."


class TestConversationLLM:
    """Test ConversationLLM class."""

    def test_conversation_llm_initialization(self) -> None:
        """Test ConversationLLM initialization."""
        llm = ConversationLLM()

        assert isinstance(llm.context_manager, ConversationContextManager)
        assert isinstance(llm.context_retriever, ContextRetriever)
        assert isinstance(llm.context_optimizer, ContextOptimizer)
        assert isinstance(llm.config, ConversationConfig)

    def test_conversation_llm_custom_config(self) -> None:
        """Test ConversationLLM with custom config."""
        config = ConversationConfig(max_history_tokens=3000)
        llm = ConversationLLM(config)

        assert llm.config.max_history_tokens == 3000

    @pytest.mark.asyncio
    async def test_chat_basic(self) -> None:
        """Test basic chat functionality."""
        llm = ConversationLLM()

        with patch("promptlifter.conversation_llm.llm_service") as mock_llm_service:
            mock_llm_service.generate = AsyncMock(
                return_value="Hello! How can I help you?"
            )

            response = await llm.chat("Hello")

            assert response.message == "Hello! How can I help you?"
            assert len(llm.context_manager.history) == 1  # One interaction

    def test_get_conversation_stats(self) -> None:
        """Test getting conversation statistics."""
        llm = ConversationLLM()

        # Add some conversation history
        llm.context_manager.add_interaction("Hello", "Hi!", ["history"])

        stats = llm.get_conversation_stats()

        assert stats["total_turns"] == 1
        assert stats["current_tokens"] > 0
        assert stats["max_history_tokens"] == 4000

    def test_clear_conversation(self) -> None:
        """Test clearing conversation."""
        llm = ConversationLLM()

        # Add some conversation history
        llm.context_manager.add_interaction("Hello", "Hi!", ["history"])

        assert len(llm.context_manager.history) == 1

        llm.clear_conversation()

        assert len(llm.context_manager.history) == 0

    def test_export_conversation(self) -> None:
        """Test exporting conversation."""
        llm = ConversationLLM()

        # Add some conversation history
        llm.context_manager.add_interaction("Hello", "Hi!", ["history"])

        exported = llm.export_conversation()

        assert len(exported) == 1
        assert exported[0]["user_message"] == "Hello"
        assert exported[0]["assistant_response"] == "Hi!"

    def test_import_conversation(self) -> None:
        """Test importing conversation."""
        llm = ConversationLLM()

        history = [
            {
                "user_message": "Hello",
                "assistant_response": "Hi!",
                "timestamp": "2024-01-01T00:00:00Z",
                "tokens_used": 5,
                "context_sources": ["history"],
            }
        ]

        llm.import_conversation(history)

        assert len(llm.context_manager.history) == 1
        assert llm.context_manager.history[0].user_message == "Hello"

    def test_get_config(self) -> None:
        """Test getting configuration."""
        llm = ConversationLLM()

        config = llm.get_config()

        assert "max_history_tokens" in config
        assert "max_context_tokens" in config
        assert "enable_auto_search" in config
        assert "search_relevance_threshold" in config
        assert "system_prompt" in config

    def test_get_retrieval_stats(self) -> None:
        """Test getting retrieval statistics."""
        llm = ConversationLLM()

        stats = llm.get_retrieval_stats()

        assert "tavily_enabled" in stats
        assert "pinecone_enabled" in stats
        assert "auto_search_enabled" in stats
        assert "relevance_threshold" in stats

    def test_get_optimization_stats(self) -> None:
        """Test getting optimization statistics."""
        llm = ConversationLLM()

        stats = llm.get_optimization_stats()

        assert "max_tokens" in stats
        assert "relevance_threshold" in stats
        assert "compression_enabled" in stats


class TestQuickChat:
    """Test quick_chat function."""

    @pytest.mark.asyncio
    async def test_quick_chat(self) -> None:
        """Test quick_chat function."""
        with patch("promptlifter.conversation_llm.ConversationLLM") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value=MagicMock(message="Quick response"))
            mock_llm_class.return_value = mock_llm

            response = await quick_chat("Test message")

            assert response == "Quick response"
            mock_llm.chat.assert_called_once_with("Test message")
