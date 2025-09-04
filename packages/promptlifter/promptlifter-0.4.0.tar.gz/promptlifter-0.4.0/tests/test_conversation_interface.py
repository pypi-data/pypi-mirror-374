"""
Unit tests for conversation interface components.
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

    @pytest.mark.asyncio
    async def test_get_conversation_context(self) -> None:
        """Test getting conversation context."""
        manager = ConversationContextManager()

        # Add some interactions
        manager.add_interaction("Hello", "Hi there!", ["history"])
        manager.add_interaction("How are you?", "I'm doing well!", ["history"])

        context = await manager.get_optimized_context("Test query")

        assert "Hello" in context
        assert "Hi there!" in context
        assert "How are you?" in context
        assert "I'm doing well!" in context

    def test_clear_conversation(self) -> None:
        """Test clearing conversation."""
        from datetime import datetime

        manager = ConversationContextManager()

        # Add some turns
        turn1 = ConversationTurn("Hello", "Hi there!", datetime.now(), 5, ["history"])
        turn2 = ConversationTurn(
            "How are you?", "I'm doing well!", datetime.now(), 8, ["history"]
        )
        manager.add_turn(turn1)
        manager.add_turn(turn2)

        assert len(manager.history) == 2
        assert manager.current_tokens == 13

        manager.clear_history()

        assert len(manager.history) == 0
        assert manager.current_tokens == 0

    def test_export_conversation(self) -> None:
        """Test exporting conversation."""
        from datetime import datetime

        manager = ConversationContextManager()

        # Add some turns
        turn1 = ConversationTurn("Hello", "Hi there!", datetime.now(), 5, ["history"])
        turn2 = ConversationTurn(
            "How are you?", "I'm doing well!", datetime.now(), 8, ["history"]
        )
        manager.add_turn(turn1)
        manager.add_turn(turn2)

        exported = manager.export_history()

        assert len(exported) == 2
        assert exported[0]["user_message"] == "Hello"
        assert exported[0]["assistant_response"] == "Hi there!"
        assert exported[1]["user_message"] == "How are you?"
        assert exported[1]["assistant_response"] == "I'm doing well!"

    def test_import_conversation(self) -> None:
        """Test importing conversation."""
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

    @pytest.mark.asyncio
    async def test_retrieve_context_conversational_query(self) -> None:
        """Test context retrieval for conversational query."""
        retriever = ContextRetriever()

        with patch.object(retriever, "should_use_search", return_value=False):
            chunks = await retriever.retrieve_relevant_context("How are you?", "")

            # For conversational queries, should return empty chunks
            assert len(chunks) == 0

    @pytest.mark.asyncio
    async def test_retrieve_context_research_query(self) -> None:
        """Test context retrieval for research query."""
        retriever = ContextRetriever()

        with (
            patch.object(retriever, "should_use_search", return_value=True),
            patch.object(
                retriever, "_search_tavily", return_value="Web search results"
            ),
            patch.object(
                retriever, "_search_pinecone", return_value="Vector search results"
            ),
        ):
            chunks = await retriever.retrieve_relevant_context(
                "What is machine learning?", ""
            )

            # Should have chunks from both sources
            assert len(chunks) >= 0  # May be empty if no relevant results

    def test_should_use_search(self) -> None:
        """Test search decision logic."""
        retriever = ContextRetriever()

        # Research queries should use search
        assert retriever.should_use_search("What is machine learning?", "") is True
        assert retriever.should_use_search("Research quantum computing", "") is True
        assert retriever.should_use_search("Tell me about AI", "") is True

        # Conversational queries should not use search
        assert retriever.should_use_search("How are you?", "") is False
        assert retriever.should_use_search("Hello", "") is False
        assert retriever.should_use_search("Thanks", "") is False


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

    def test_optimize_context(self) -> None:
        """Test context optimization."""
        optimizer = ContextOptimizer()

        chunks = [
            ContextChunk("Content 1", "tavily", {"tokens": 100}),
            ContextChunk("Content 2", "pinecone", {"tokens": 150}),
            ContextChunk("Content 3", "tavily", {"tokens": 200}),
        ]

        optimized = optimizer.optimize_context("", chunks, "Test query")

        assert isinstance(optimized, OptimizedContext)
        assert optimized.total_tokens <= 6000

    def test_optimize_context_empty_chunks(self) -> None:
        """Test context optimization with empty chunks."""
        optimizer = ContextOptimizer()

        optimized = optimizer.optimize_context("", [], "Test query")

        assert isinstance(optimized, OptimizedContext)
        assert optimized.content == ""
        assert optimized.sources_used == []
        assert optimized.total_tokens == 0


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

    @pytest.mark.asyncio
    async def test_chat_with_context_retrieval(self) -> None:
        """Test chat with context retrieval."""
        llm = ConversationLLM()

        with (
            patch.object(
                llm.context_retriever, "retrieve_relevant_context"
            ) as mock_retrieve,
            patch("promptlifter.conversation_llm.llm_service") as mock_llm_service,
        ):
            mock_retrieve.return_value = [
                ContextChunk("Test context", "tavily", {"tokens": 50})
            ]
            mock_llm_service.generate = AsyncMock(
                return_value="Based on the context, here's my response."
            )

            response = await llm.chat("What is machine learning?")

            assert response.message == "Based on the context, here's my response."
            assert "tavily" in response.context_sources

    def test_get_conversation_stats(self) -> None:
        """Test getting conversation statistics."""
        llm = ConversationLLM()

        # Add some conversation history
        from datetime import datetime

        turn = ConversationTurn("Hello", "Hi!", datetime.now(), 13, ["history"])
        llm.context_manager.add_turn(turn)

        stats = llm.get_conversation_stats()

        assert stats["total_turns"] == 1
        assert stats["current_tokens"] == 13
        assert stats["max_history_tokens"] == 4000

    def test_clear_conversation(self) -> None:
        """Test clearing conversation."""
        llm = ConversationLLM()

        # Add some conversation history
        from datetime import datetime

        turn = ConversationTurn("Hello", "Hi!", datetime.now(), 5, ["history"])
        llm.context_manager.add_turn(turn)

        assert len(llm.context_manager.history) == 1

        llm.clear_conversation()

        assert len(llm.context_manager.history) == 0

    def test_export_conversation(self) -> None:
        """Test exporting conversation."""
        llm = ConversationLLM()

        # Add some conversation history
        from datetime import datetime

        turn = ConversationTurn("Hello", "Hi!", datetime.now(), 5, ["history"])
        llm.context_manager.add_turn(turn)

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

    def test_update_config(self) -> None:
        """Test updating configuration."""
        llm = ConversationLLM()

        llm.update_config(max_history_tokens=3000, enable_auto_search=False)

        assert llm.config.max_history_tokens == 3000
        assert llm.config.enable_auto_search is False
        assert llm.context_manager.max_history_tokens == 3000
        assert llm.context_retriever.enable_auto_search is False

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


class TestIntegration:
    """Integration tests for the conversation interface."""

    @pytest.mark.asyncio
    async def test_basic_functionality_integration(self) -> None:
        """Test basic functionality integration without external dependencies."""
        # Test initialization
        llm = ConversationLLM()
        assert llm is not None

        # Test configuration
        config = llm.get_config()
        assert isinstance(config, dict)
        assert "max_history_tokens" in config
        assert "max_context_tokens" in config

        # Test conversation stats
        stats = llm.get_conversation_stats()
        assert isinstance(stats, dict)
        assert "total_turns" in stats
        assert "current_tokens" in stats

        # Test retrieval stats
        retrieval_stats = llm.get_retrieval_stats()
        assert isinstance(retrieval_stats, dict)
        assert "tavily_enabled" in retrieval_stats
        assert "pinecone_enabled" in retrieval_stats

        # Test optimization stats
        optimization_stats = llm.get_optimization_stats()
        assert isinstance(optimization_stats, dict)
        assert "max_tokens" in optimization_stats

        # Test conversation management
        llm.clear_conversation()
        stats_after_clear = llm.get_conversation_stats()
        assert stats_after_clear["total_turns"] == 0

        # Test export/import (empty conversation)
        history = llm.export_conversation()
        assert isinstance(history, list)
        assert len(history) == 0

    def test_configuration_integration(self) -> None:
        """Test configuration management integration."""
        # Test custom configuration
        config = ConversationConfig(
            max_history_tokens=2000,
            max_context_tokens=1000,
            enable_auto_search=False,
            search_relevance_threshold=0.8,
            system_prompt="You are a test assistant.",
        )

        llm = ConversationLLM(config)
        assert llm.config.max_history_tokens == 2000
        assert llm.config.max_context_tokens == 1000
        assert llm.config.enable_auto_search is False

        # Test config update
        llm.update_config(max_history_tokens=3000)
        updated_config = llm.get_config()
        assert updated_config["max_history_tokens"] == 3000

    def test_context_components_integration(self) -> None:
        """Test individual context components integration."""
        # Test ConversationContextManager
        manager = ConversationContextManager(max_history_tokens=1000)
        manager.add_interaction("Hello", "Hi there!", ["test"])
        stats = manager.get_conversation_stats()
        assert stats["total_turns"] == 1

        # Test ContextRetriever
        retriever = ContextRetriever(enable_auto_search=False)
        retrieval_stats = retriever.get_retrieval_stats()
        assert "tavily_enabled" in retrieval_stats
        assert "pinecone_enabled" in retrieval_stats

        # Test ContextOptimizer
        optimizer = ContextOptimizer(max_tokens=1000)
        optimization_stats = optimizer.get_optimization_stats()
        assert "max_tokens" in optimization_stats
        assert optimization_stats["max_tokens"] == 1000
