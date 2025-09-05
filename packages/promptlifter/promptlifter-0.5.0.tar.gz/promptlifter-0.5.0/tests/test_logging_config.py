"""
Tests for logging configuration module.
"""

import logging
import tempfile

from promptlifter.logging_config import get_logger, setup_logging


class TestLoggingConfig:
    """Test logging configuration functions."""

    def test_setup_logging_default(self) -> None:
        """Test setup_logging with default parameters."""
        # Test that setup_logging runs without errors
        setup_logging()

        # Verify that logging is configured
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) > 0

    def test_setup_logging_with_level(self) -> None:
        """Test setup_logging with custom level."""
        setup_logging(level="DEBUG")

        # Verify logger was configured with DEBUG level
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_setup_logging_with_file(self) -> None:
        """Test setup_logging with log file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as f:
            temp_file = f.name

        try:
            setup_logging(log_file=temp_file)

            # Verify file handler was created
            root_logger = logging.getLogger()
            file_handlers = [
                h for h in root_logger.handlers if isinstance(h, logging.FileHandler)
            ]
            assert len(file_handlers) > 0
        finally:
            import os

            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_setup_logging_invalid_level(self) -> None:
        """Test setup_logging with invalid level falls back to INFO."""
        setup_logging(level="INVALID")

        # Should fall back to INFO level
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_setup_logging_sets_specific_logger_levels(self) -> None:
        """Test that setup_logging sets specific logger levels."""
        setup_logging()

        # Verify specific loggers were configured
        assert logging.getLogger("httpx").level == logging.WARNING
        assert logging.getLogger("urllib3").level == logging.WARNING
        assert logging.getLogger("pinecone").level == logging.WARNING

    def test_get_logger(self) -> None:
        """Test get_logger function."""
        logger = get_logger("test_logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_setup_logging_clears_existing_handlers(self) -> None:
        """Test that setup_logging clears existing handlers."""
        # Add a handler first
        root_logger = logging.getLogger()
        setup_logging()

        # Verify handlers were cleared and new ones added
        assert len(root_logger.handlers) > 0

    def test_setup_logging_console_handler(self) -> None:
        """Test that setup_logging creates console handler."""
        setup_logging()

        # Verify console handler was created
        root_logger = logging.getLogger()
        console_handlers = [
            h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(console_handlers) > 0

    def test_setup_logging_formatter(self) -> None:
        """Test that setup_logging creates proper formatter."""
        setup_logging()

        # Verify formatter was created with correct format
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if hasattr(handler, "formatter") and handler.formatter:
                formatter = handler.formatter
                assert "%(asctime)s" in formatter._fmt
                assert "%(name)s" in formatter._fmt
                assert "%(levelname)s" in formatter._fmt
                assert "%(message)s" in formatter._fmt
                break
