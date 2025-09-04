"""
Unit tests for embedding service module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from promptlifter.nodes.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Test EmbeddingService class."""

    def test_embedding_service_initialization(self) -> None:
        """Test EmbeddingService initialization."""
        service = EmbeddingService()
        # Test that the service initializes with the mock values from CI
        assert service.embedding_provider is not None
        assert service.embedding_model is not None
        assert service.custom_endpoint is not None
        assert service.custom_model is not None
        assert service.custom_api_key is not None

    @pytest.mark.asyncio
    async def test_openai_embedding_success(self) -> None:
        """Test successful OpenAI embedding generation."""
        with patch(
            "promptlifter.nodes.embedding_service.httpx.AsyncClient"
        ) as mock_client:
            # Mock OpenAI API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [0.1]}
                ]  # 1536 dimensions
            }

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = EmbeddingService()
            result = await service._get_openai_embedding("test text")

            assert result is not None
            assert len(result) == 1536
            assert all(isinstance(x, float) for x in result)

    @pytest.mark.asyncio
    async def test_openai_embedding_failure(self) -> None:
        """Test OpenAI embedding failure handling."""
        with patch(
            "promptlifter.nodes.embedding_service.httpx.AsyncClient"
        ) as mock_client:
            # Mock OpenAI API failure
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": {"message": "Invalid API key"}}

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = EmbeddingService()
            result = await service._get_openai_embedding("test text")

            assert result is None

    @pytest.mark.asyncio
    async def test_custom_embedding_lambda_success(self) -> None:
        """Test successful custom embedding with Lambda Labs."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_LLM_API_KEY": "test-key",
                "CUSTOM_LLM_ENDPOINT": "https://api.lambda.ai/v1",
            },
        ):
            # Reload config to pick up the new environment variables
            import importlib

            import promptlifter.config

            importlib.reload(promptlifter.config)

            # Also reload the embedding service module
            import sys

            embedding_service_module = sys.modules[
                "promptlifter.nodes.embedding_service"
            ]
            importlib.reload(embedding_service_module)

            # Import the class after reloading
            from promptlifter.nodes.embedding_service import EmbeddingService

            with patch(
                "promptlifter.nodes.embedding_service.httpx.AsyncClient"
            ) as mock_client:
                # Mock Lambda Labs API response
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "data": [{"embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [0.1]}]
                }

                mock_client_instance = MagicMock()
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client_instance.__aexit__.return_value = None
                mock_client_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_client_instance

                service = EmbeddingService()
                result = await service._get_custom_embedding("test text")

                assert result is not None
                assert len(result) == 1536
                assert all(isinstance(x, float) for x in result)

    @pytest.mark.asyncio
    async def test_custom_embedding_model_fallback(self) -> None:
        """Test custom embedding with model fallback."""
        with patch.dict(
            "os.environ",
            {
                "CUSTOM_LLM_API_KEY": "test-key",
                "CUSTOM_LLM_ENDPOINT": "https://api.lambda.ai/v1",
            },
        ):
            # Reload config to pick up the new environment variables
            import importlib

            import promptlifter.config

            importlib.reload(promptlifter.config)

            # Also reload the embedding service module
            import sys

            embedding_service_module = sys.modules[
                "promptlifter.nodes.embedding_service"
            ]
            importlib.reload(embedding_service_module)

            # Import the class after reloading
            from promptlifter.nodes.embedding_service import EmbeddingService

            with patch(
                "promptlifter.nodes.embedding_service.httpx.AsyncClient"
            ) as mock_client:
                # Mock first model failure, second model success
                mock_response_fail = MagicMock()
                mock_response_fail.status_code = 400
                mock_response_fail.json.return_value = {
                    "error": {"message": "Model not found"}
                }

                mock_response_success = MagicMock()
                mock_response_success.status_code = 200
                mock_response_success.json.return_value = {
                    "data": [{"embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [0.1]}]
                }

                mock_client_instance = MagicMock()
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client_instance.__aexit__.return_value = None
                mock_client_instance.post = AsyncMock(
                    side_effect=[mock_response_fail, mock_response_success]
                )
                mock_client.return_value = mock_client_instance

                service = EmbeddingService()
                result = await service._get_custom_embedding("test text")

                assert result is not None
                assert len(result) == 1536

    @pytest.mark.asyncio
    async def test_custom_embedding_ollama_success(self) -> None:
        """Test successful custom embedding with Ollama-style API."""
        with patch.dict(
            "os.environ",
            {"CUSTOM_LLM_API_KEY": "", "CUSTOM_LLM_ENDPOINT": "http://localhost:11434"},
        ):
            # Reload config to pick up the new environment variables
            import importlib

            import promptlifter.config

            importlib.reload(promptlifter.config)

            # Also reload the embedding service module
            import sys

            embedding_service_module = sys.modules[
                "promptlifter.nodes.embedding_service"
            ]
            importlib.reload(embedding_service_module)

            # Import the class after reloading
            from promptlifter.nodes.embedding_service import EmbeddingService

            with patch(
                "promptlifter.nodes.embedding_service.httpx.AsyncClient"
            ) as mock_client:
                # Mock Ollama API response
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [0.1]
                }

                mock_client_instance = MagicMock()
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client_instance.__aexit__.return_value = None
                mock_client_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_client_instance

                service = EmbeddingService()
                result = await service._get_custom_embedding("test text")

                assert result is not None
                assert len(result) == 1536

    def test_fallback_embedding(self) -> None:
        """Test fallback embedding generation."""
        service = EmbeddingService()
        result = service._fallback_embedding("test text for embedding")

        assert result is not None
        assert len(result) == 1536
        assert all(isinstance(x, float) for x in result)
        # Fallback embeddings should be deterministic for same input
        result2 = service._fallback_embedding("test text for embedding")
        assert result == result2

    @pytest.mark.asyncio
    async def test_embed_text_custom_success(self) -> None:
        """Test embed_text with successful custom embedding."""
        with patch.dict("os.environ", {"EMBEDDING_PROVIDER": "custom"}):
            # Reload config to pick up the new environment variable
            import importlib

            import promptlifter.config

            importlib.reload(promptlifter.config)

            # Also reload the embedding service module
            import sys

            embedding_service_module = sys.modules[
                "promptlifter.nodes.embedding_service"
            ]
            importlib.reload(embedding_service_module)

            # Import the class after reloading
            from promptlifter.nodes.embedding_service import EmbeddingService

            with patch.object(EmbeddingService, "_get_custom_embedding") as mock_custom:
                mock_custom.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [
                    0.1
                ]  # 1536 dimensions

                service = EmbeddingService()
                result = await service.embed_text("test text")

                assert result is not None
                assert len(result) == 1536
                mock_custom.assert_called_once_with("test text")

    @pytest.mark.asyncio
    async def test_embed_text_openai_fallback(self) -> None:
        """Test embed_text with OpenAI failure and fallback."""
        with patch.object(EmbeddingService, "_get_openai_embedding") as mock_openai:
            mock_openai.return_value = None

            service = EmbeddingService()
            result = await service.embed_text("test text")

            assert result is not None
            assert len(result) == 1536
            # Should use fallback embedding
            assert result != [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [0.1]

    @pytest.mark.asyncio
    async def test_embed_text_anthropic_success(self) -> None:
        """Test embed_text with successful Anthropic embedding."""
        with patch.dict("os.environ", {"EMBEDDING_PROVIDER": "anthropic"}):
            # Reload config to pick up the new environment variable
            import importlib

            import promptlifter.config

            importlib.reload(promptlifter.config)

            # Also reload the embedding service module
            import sys

            embedding_service_module = sys.modules[
                "promptlifter.nodes.embedding_service"
            ]
            importlib.reload(embedding_service_module)

            # Import the class after reloading
            from promptlifter.nodes.embedding_service import EmbeddingService

            with patch.object(
                EmbeddingService, "_get_anthropic_embedding"
            ) as mock_anthropic:
                mock_anthropic.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [
                    0.1
                ]  # 1536 dimensions

                service = EmbeddingService()
                result = await service.embed_text("test text")

                assert result is not None
                assert len(result) == 1536
                mock_anthropic.assert_called_once_with("test text")

    @pytest.mark.asyncio
    async def test_embed_text_unknown_provider_fallback(self) -> None:
        """Test embed_text with unknown provider falls back to fallback embedding."""
        service = EmbeddingService()
        result = await service.embed_text("test text")

        assert result is not None
        assert len(result) == 1536

    @pytest.mark.asyncio
    async def test_embed_text_empty_input(self) -> None:
        """Test embed_text with empty input."""
        service = EmbeddingService()
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await service.embed_text("")

    @pytest.mark.asyncio
    async def test_embed_text_long_input(self) -> None:
        """Test embed_text with long input text."""
        with patch.dict("os.environ", {"EMBEDDING_PROVIDER": "openai"}):
            # Reload config to pick up the new environment variable
            import importlib

            import promptlifter.config

            importlib.reload(promptlifter.config)

            # Also reload the embedding service module
            import sys

            embedding_service_module = sys.modules[
                "promptlifter.nodes.embedding_service"
            ]
            importlib.reload(embedding_service_module)

            # Import the class after reloading
            from promptlifter.nodes.embedding_service import EmbeddingService

            long_text = "This is a very long text " * 1000  # ~25k characters

            with patch.object(EmbeddingService, "_get_openai_embedding") as mock_openai:
                mock_openai.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [
                    0.1
                ]  # 1536 dimensions

                service = EmbeddingService()
                result = await service.embed_text(long_text)

                assert result is not None
                assert len(result) == 1536
                mock_openai.assert_called_once_with(long_text)

    @pytest.mark.asyncio
    async def test_embed_text_special_characters(self) -> None:
        """Test embed_text with special characters."""
        with patch.dict("os.environ", {"EMBEDDING_PROVIDER": "openai"}):
            # Reload config to pick up the new environment variable
            import importlib

            import promptlifter.config

            importlib.reload(promptlifter.config)

            # Also reload the embedding service module
            import sys

            embedding_service_module = sys.modules[
                "promptlifter.nodes.embedding_service"
            ]
            importlib.reload(embedding_service_module)

            # Import the class after reloading
            from promptlifter.nodes.embedding_service import EmbeddingService

            special_text = "Test with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"

            with patch.object(EmbeddingService, "_get_openai_embedding") as mock_openai:
                mock_openai.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [
                    0.1
                ]  # 1536 dimensions

                service = EmbeddingService()
                result = await service.embed_text(special_text)

                assert result is not None
                assert len(result) == 1536
                mock_openai.assert_called_once_with(special_text)
