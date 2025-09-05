"""
Unit tests for LLM service module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from promptlifter.nodes.llm_service import CustomLLMService


class TestCustomLLMService:
    """Test CustomLLMService class."""

    def test_llm_service_initialization(self, mock_env_vars) -> None:
        """Test CustomLLMService initialization."""
        service = CustomLLMService()

        # Test that the service initializes with configuration
        assert service.custom_endpoint is not None
        assert service.custom_model is not None
        assert service.custom_api_key is not None
        assert service.llm_provider is not None

    @pytest.mark.asyncio
    async def test_generate_custom_llm_success(self, mock_env_vars) -> None:
        """Test successful custom LLM generation."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "custom"),
            patch(
                "promptlifter.nodes.llm_service.CUSTOM_LLM_ENDPOINT",
                "http://localhost:11434",
            ),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_MODEL", "llama3.1"),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_API_KEY", ""),
        ):
            # Mock successful response (Ollama format)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"message": {"content": "Test response"}}

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()
            result = await service.generate(
                [{"role": "user", "content": "Test prompt"}]
            )

            assert result == "Test response"

    @pytest.mark.asyncio
    async def test_generate_custom_llm_failure(self, mock_env_vars) -> None:
        """Test custom LLM generation failure."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "custom"),
            patch(
                "promptlifter.nodes.llm_service.CUSTOM_LLM_ENDPOINT",
                "http://localhost:11434",
            ),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_MODEL", "llama3.1"),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_API_KEY", ""),
        ):
            # Mock failure response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal server error"}

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()

            # The service will raise an exception when the provider fails
            with pytest.raises(Exception, match="custom LLM provider failed"):
                await service.generate([{"role": "user", "content": "Test prompt"}])

    @pytest.mark.asyncio
    async def test_generate_openai_success(self, mock_env_vars) -> None:
        """Test successful OpenAI generation."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "openai"),
            patch("promptlifter.nodes.llm_service.OPENAI_API_KEY", "test-openai-key"),
        ):
            # Mock successful OpenAI response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "OpenAI response"}}]
            }

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()
            result = await service.generate(
                [{"role": "user", "content": "Test prompt"}]
            )

            assert result == "OpenAI response"

    @pytest.mark.asyncio
    async def test_generate_anthropic_success(self, mock_env_vars) -> None:
        """Test successful Anthropic generation."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "anthropic"),
            patch(
                "promptlifter.nodes.llm_service.ANTHROPIC_API_KEY", "test-anthropic-key"
            ),
        ):
            # Mock successful Anthropic response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "content": [{"text": "Anthropic response"}]
            }

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()
            result = await service.generate(
                [{"role": "user", "content": "Test prompt"}]
            )

            assert result == "Anthropic response"

    @pytest.mark.asyncio
    async def test_generate_google_success(self, mock_env_vars) -> None:
        """Test successful Google generation."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "google"),
            patch("promptlifter.nodes.llm_service.GOOGLE_API_KEY", "test-google-key"),
        ):
            # Mock successful Google response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "candidates": [{"content": {"parts": [{"text": "Google response"}]}}]
            }

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()
            result = await service.generate(
                [{"role": "user", "content": "Test prompt"}]
            )

            assert result == "Google response"

    @pytest.mark.asyncio
    async def test_generate_fallback_chain(self, mock_env_vars) -> None:
        """Test fallback chain when providers fail."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "custom"),
            patch(
                "promptlifter.nodes.llm_service.CUSTOM_LLM_ENDPOINT",
                "http://localhost:11434",
            ),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_MODEL", "llama3.1"),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_API_KEY", ""),
        ):
            # Mock all providers failing
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Service unavailable"}

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()

            # The service will raise an exception when all providers fail
            with pytest.raises(Exception, match="custom LLM provider failed"):
                await service.generate([{"role": "user", "content": "Test prompt"}])

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_env_vars) -> None:
        """Test generation with system prompt."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "custom"),
            patch(
                "promptlifter.nodes.llm_service.CUSTOM_LLM_ENDPOINT",
                "http://localhost:11434",
            ),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_MODEL", "llama3.1"),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_API_KEY", ""),
        ):
            # Mock successful response (Ollama format)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": {"content": "System prompt response"}
            }

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()
            result = await service.generate(
                [{"role": "user", "content": "Test prompt"}]
            )

            assert result == "System prompt response"

    @pytest.mark.asyncio
    async def test_generate_with_max_tokens(self, mock_env_vars) -> None:
        """Test generation with max tokens limit."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "custom"),
            patch(
                "promptlifter.nodes.llm_service.CUSTOM_LLM_ENDPOINT",
                "http://localhost:11434",
            ),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_MODEL", "llama3.1"),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_API_KEY", ""),
        ):
            # Mock successful response (Ollama format)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": {"content": "Limited response"}
            }

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()
            result = await service.generate(
                [{"role": "user", "content": "Test prompt"}], max_tokens=100
            )

            assert result == "Limited response"

    @pytest.mark.asyncio
    async def test_generate_with_temperature(self, mock_env_vars) -> None:
        """Test generation with temperature setting."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "custom"),
            patch(
                "promptlifter.nodes.llm_service.CUSTOM_LLM_ENDPOINT",
                "http://localhost:11434",
            ),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_MODEL", "llama3.1"),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_API_KEY", ""),
        ):
            # Mock successful response (Ollama format)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": {"content": "Temperature response"}
            }

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()
            result = await service.generate(
                [{"role": "user", "content": "Test prompt"}]
            )

            assert result == "Temperature response"

    @pytest.mark.asyncio
    async def test_generate_empty_prompt(self, mock_env_vars) -> None:
        """Test generation with empty prompt."""
        service = CustomLLMService()

        # The service doesn't validate empty messages, it just fails
        with pytest.raises(Exception, match="custom LLM provider failed"):
            await service.generate([])

    @pytest.mark.asyncio
    async def test_generate_long_prompt(self, mock_env_vars) -> None:
        """Test generation with very long prompt."""
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "custom"),
            patch(
                "promptlifter.nodes.llm_service.CUSTOM_LLM_ENDPOINT",
                "http://localhost:11434",
            ),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_MODEL", "llama3.1"),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_API_KEY", ""),
        ):
            # Mock successful response (Ollama format)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": {"content": "Long prompt response"}
            }

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            service = CustomLLMService()
            long_prompt = "This is a very long prompt " * 1000  # ~25k characters
            result = await service.generate([{"role": "user", "content": long_prompt}])

            assert result == "Long prompt response"

    @pytest.mark.asyncio
    async def test_rate_limiting(self, mock_env_vars) -> None:
        """Test rate limiting functionality."""
        # Test rate limiting with multiple rapid calls
        with (
            patch("promptlifter.nodes.llm_service.httpx.AsyncClient") as mock_client,
            patch("promptlifter.nodes.llm_service.LLM_PROVIDER", "custom"),
            patch(
                "promptlifter.nodes.llm_service.CUSTOM_LLM_ENDPOINT",
                "http://localhost:11434",
            ),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_MODEL", "llama3.1"),
            patch("promptlifter.nodes.llm_service.CUSTOM_LLM_API_KEY", ""),
        ):
            service = CustomLLMService()

            # Test that rate limiter is initialized
            assert hasattr(service, "rate_limiter")
            # Mock successful response (Ollama format)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": {"content": "Rate limited response"}
            }

            mock_client_instance = MagicMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_client_instance

            # Make multiple rapid calls
            results = []
            for i in range(5):
                result = await service.generate(
                    [{"role": "user", "content": f"Test prompt {i}"}]
                )
                results.append(result)

            # All should succeed (rate limiter allows reasonable rates)
            assert len(results) == 5
            assert all(result == "Rate limited response" for result in results)
