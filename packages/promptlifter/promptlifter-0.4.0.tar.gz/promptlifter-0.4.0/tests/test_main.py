"""
Tests for main application module.
"""

import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from promptlifter.main import (
    interactive_mode,
    main,
    print_result_summary,
    save_result_to_file,
    validate_configuration,
)


class TestMainFunctions:
    """Test main application functions."""

    def test_validate_configuration_success(self) -> None:
        """Test validate_configuration with valid config."""
        # Mock environment variables for successful validation
        with patch.dict(
            "os.environ", {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"}
        ):
            # Should not raise any exception
            validate_configuration()

    def test_validate_configuration_failure(self) -> None:
        """Test validate_configuration with invalid config."""
        # Clear environment to cause validation failure
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                validate_configuration()

            assert exc_info.value.code == 1

    def test_save_result_to_file(self) -> None:
        """Test save_result_to_file function."""
        test_response = MagicMock()
        test_response.message = "Test response"
        test_response.context_sources = ["history"]
        test_response.tokens_used = 50
        test_response.conversation_stats = {"total_turns": 1}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name

        try:
            save_result_to_file(test_response, temp_file)

            # Verify file was created
            import os

            assert os.path.exists(temp_file)
        finally:
            import os

            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_print_result_summary(self) -> None:
        """Test print_result_summary function."""
        test_response = MagicMock()
        test_response.message = "Test response"
        test_response.context_sources = ["history"]
        test_response.tokens_used = 50
        test_response.conversation_stats = {"total_turns": 1}

        with patch("builtins.print") as mock_print:
            print_result_summary(test_response)

            # Verify print was called
            mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_interactive_mode(self) -> None:
        """Test interactive_mode function."""
        with (
            patch("promptlifter.main.ConversationLLM") as mock_llm_class,
            patch("builtins.input") as mock_input,
        ):

            mock_llm = AsyncMock()
            mock_llm.chat.return_value = MagicMock(
                message="Test response",
                context_sources=["history"],
                tokens_used=50,
                conversation_stats={},
            )
            mock_llm_class.return_value = mock_llm

            # Mock input to return "exit" immediately to avoid blocking
            mock_input.side_effect = ["exit"]

            await interactive_mode()

            # Verify LLM was not called since we exited immediately
            mock_llm.chat.assert_not_called()

    @pytest.mark.asyncio
    async def test_interactive_mode_with_query(self) -> None:
        """Test interactive_mode function with a query."""
        with (
            patch("promptlifter.main.ConversationLLM") as mock_llm_class,
            patch("builtins.input") as mock_input,
        ):

            mock_llm = AsyncMock()
            mock_llm.chat.return_value = MagicMock(
                message="Test response",
                context_sources=["history"],
                tokens_used=50,
                conversation_stats={},
            )
            mock_llm_class.return_value = mock_llm

            # Mock input sequence: query, save choice (no), then exit
            mock_input.side_effect = ["Test query", "n", "exit"]

            await interactive_mode()

            # Verify LLM was called with the query
            mock_llm.chat.assert_called_once_with("Test query")

    def test_main_basic(self) -> None:
        """Test main function basic execution."""
        with (
            patch("promptlifter.main.validate_configuration") as mock_validate,
            patch("promptlifter.main.interactive_mode") as mock_interactive,
            patch("promptlifter.main.setup_logging") as mock_logging,
            patch("sys.argv", ["main.py", "--interactive"]),
        ):

            mock_interactive.return_value = None

            main()

            # Verify basic setup was called
            mock_logging.assert_called_once()
            mock_validate.assert_called_once()
            mock_interactive.assert_called_once()

    def test_main_config_validation_error(self) -> None:
        """Test main function with configuration validation error."""
        with (
            patch("promptlifter.main.validate_configuration") as mock_validate,
            patch("sys.argv", ["main.py", "--interactive"]),
        ):

            mock_validate.side_effect = SystemExit(1)

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
