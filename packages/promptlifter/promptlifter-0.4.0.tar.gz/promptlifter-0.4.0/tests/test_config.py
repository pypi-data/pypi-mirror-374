"""
Unit tests for configuration module.
"""

import os
from unittest.mock import patch

from promptlifter.config import validate_config, validate_url


class TestConfigValidation:
    """Test configuration validation functions."""

    def test_validate_url_valid(self) -> None:
        """Test URL validation with valid URLs."""
        valid_urls = [
            "http://localhost:11434",
            "https://api.openai.com",
            "https://api.lambda.ai/v1",
            "http://127.0.0.1:8000",
        ]

        for url in valid_urls:
            assert validate_url(url) is True

    def test_validate_url_invalid(self) -> None:
        """Test URL validation with invalid URLs."""
        invalid_urls = ["not-a-url", "localhost", ""]

        for url in invalid_urls:
            assert validate_url(url) is False

    def test_validate_url_edge_cases(self) -> None:
        """Test URL validation with edge cases."""
        # ftp://invalid might be considered valid by urllib.parse
        # so we test it separately
        assert (
            validate_url("ftp://invalid") is True
        )  # This is actually valid URL format

    @patch.dict(
        os.environ,
        {
            "CUSTOM_LLM_ENDPOINT": "http://localhost:11434",
            "CUSTOM_LLM_MODEL": "llama3.1",
        },
    )
    def test_validate_config_valid(self) -> None:
        """Test configuration validation with valid settings."""
        errors = validate_config()
        assert len(errors) == 0

    @patch.dict(
        os.environ, {"CUSTOM_LLM_ENDPOINT": "invalid-url", "CUSTOM_LLM_MODEL": ""}
    )
    def test_validate_config_invalid(self) -> None:
        """Test configuration validation with invalid settings."""
        errors = validate_config()
        assert len(errors) > 0
        assert any("CUSTOM_LLM_ENDPOINT" in error for error in errors)
        assert any("CUSTOM_LLM_MODEL" in error for error in errors)

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_config_no_providers(self) -> None:
        """Test configuration validation with no LLM providers."""
        errors = validate_config()
        assert len(errors) > 0
        assert any("LLM provider" in error for error in errors)
