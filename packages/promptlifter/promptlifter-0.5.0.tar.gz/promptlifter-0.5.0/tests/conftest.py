"""
Pytest configuration and fixtures for PromptLifter tests.
"""

import os
from typing import Any, Generator
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_env_vars() -> Generator[dict[str, str], None, None]:
    """Mock environment variables for testing."""
    env_vars = {
        # Custom LLM Configuration (Primary - Local Models)
        "CUSTOM_LLM_ENDPOINT": "http://localhost:11434",
        "CUSTOM_LLM_MODEL": "llama3.1",
        "CUSTOM_LLM_API_KEY": "",
        # LLM Provider Configuration
        "LLM_PROVIDER": "custom",
        # Embedding Configuration
        "EMBEDDING_PROVIDER": "custom",
        "EMBEDDING_MODEL": "nomic-embed-text",
        # Commercial LLM Configuration (Fallback)
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "GOOGLE_API_KEY": "test-google-key",
        # Search and Vector Configuration
        "TAVILY_API_KEY": "test-tavily-key",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_INDEX": "test-index",
        "PINECONE_NAMESPACE": "test-namespace",
        # Pinecone Search Configuration
        "PINECONE_TOP_K": "10",
        "PINECONE_SIMILARITY_THRESHOLD": "0.7",
        "PINECONE_INCLUDE_SCORES": "true",
        "PINECONE_FILTER_BY_SCORE": "true",
        # Conversation Context Configuration
        "MAX_HISTORY_TOKENS": "4000",
        "MAX_CONTEXT_TOKENS": "2000",
        "ENABLE_AUTO_SEARCH": "true",
        "SEARCH_RELEVANCE_THRESHOLD": "0.7",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_state() -> dict[str, Any]:
    """Sample state for testing."""
    return {
        "input": "What is machine learning?",
        "subtasks": [
            "What is machine learning?",
            "How does machine learning work?",
            "What are the applications of machine learning?",
        ],
        "original_query": "What is machine learning?",
        "subtask_results": [
            {
                "task": "What is machine learning?",
                "result": "Machine learning is a subset of artificial intelligence...",
                "tavily_data": "Web search results about ML...",
                "pinecone_data": "Knowledge base results about ML...",
            },
            {
                "task": "How does machine learning work?",
                "result": "Machine learning works by training algorithms...",
                "tavily_data": "Web search results about how ML works...",
                "pinecone_data": "Knowledge base results about ML algorithms...",
            },
        ],
        "final_output": "",
        "subtask_count": 0,
        "error": None,
    }


@pytest.fixture
def mock_llm_response() -> str:
    """Mock LLM response for testing."""
    return (
        "- What is machine learning?\n"
        "- How does machine learning work?\n"
        "- What are the applications of machine learning?"
    )


@pytest.fixture
def mock_search_results() -> dict[str, str]:
    """Mock search results for testing."""
    return {
        "tavily": (
            "Machine learning is a subset of artificial intelligence that enables "
            "computers to learn and improve from experience without being explicitly "
            "programmed."
        ),
        "pinecone": (
            "Machine learning algorithms build mathematical models based on sample "
            "data to make predictions or decisions without being explicitly "
            "programmed to perform the task."
        ),
    }
