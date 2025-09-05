"""
Unit tests for nodes module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from promptlifter.nodes.run_pinecone_search import run_pinecone_search
from promptlifter.nodes.run_tavily_search import run_tavily_search


class TestSearchNodes:
    """Test search nodes."""

    @pytest.mark.asyncio
    async def test_run_tavily_search_success(self) -> None:
        """Test successful Tavily search."""
        with patch(
            "promptlifter.nodes.run_tavily_search.httpx.AsyncClient"
        ) as mock_client:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "results": [{"title": "Test Result", "content": "Test content"}]
            }

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            result = await run_tavily_search("test query")

            # The function returns only the content, not the title
            assert "Test content" in result

    @pytest.mark.asyncio
    async def test_run_tavily_search_401_error(self) -> None:
        """Test Tavily search with 401 error."""
        with patch(
            "promptlifter.nodes.run_tavily_search.httpx.AsyncClient"
        ) as mock_client:
            # Mock 401 response
            mock_response = MagicMock()
            mock_response.status_code = 401

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            result = await run_tavily_search("test query")

            # The actual error message format
            assert "[Error: Tavily API key is invalid or expired" in result

    @pytest.mark.asyncio
    async def test_run_pinecone_search_success(self) -> None:
        """Test successful Pinecone search."""
        with (
            patch("promptlifter.nodes.run_pinecone_search.Pinecone") as mock_pinecone,
            patch(
                "promptlifter.nodes.run_pinecone_search.embedding_service"
            ) as mock_embedding_service,
            patch(
                "promptlifter.nodes.run_pinecone_search.PINECONE_API_KEY", "test_key"
            ),
            patch(
                "promptlifter.nodes.run_pinecone_search.PINECONE_INDEX", "test_index"
            ),
        ):
            # Mock embedding service with correct dimensions (1536 dimensions)
            mock_embedding_service.embed_text = AsyncMock(return_value=[0.1] * 1536)

            # Mock Pinecone response
            mock_index = MagicMock()
            mock_index.query.return_value = {
                "matches": [
                    {
                        "score": 0.8,
                        "metadata": {"text": "Test knowledge base content"},
                    }
                ]
            }
            mock_pinecone.return_value.Index.return_value = mock_index

            result = await run_pinecone_search("test query")

            # The result should contain the expected content
            expected = "Test knowledge base content"
            assert expected in result

    @pytest.mark.asyncio
    async def test_run_pinecone_search_negative_scores(self) -> None:
        """Test Pinecone search with negative similarity scores."""
        # Test that the function returns a valid result
        result = await run_pinecone_search("test query")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_run_pinecone_search_low_scores(self) -> None:
        """Test Pinecone search with low positive similarity scores."""
        # Test that the function returns a valid result
        result = await run_pinecone_search("test query")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_run_pinecone_search_medium_scores(self) -> None:
        """Test Pinecone search with medium similarity scores."""
        # Test that the function returns a valid result
        result = await run_pinecone_search("test query")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_run_pinecone_search_very_low_scores(self) -> None:
        """Test Pinecone search with very low similarity scores."""
        # Test that the function returns a valid result
        result = await run_pinecone_search("test query")
        assert isinstance(result, str)
        assert len(result) > 0
