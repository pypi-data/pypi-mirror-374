"""Centralized logging utilities for b10-transfer package with colored output."""

import logging
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors and b10-transfer prefix to log messages."""

    # ANSI color codes
    COLORS = {
        "cyan": "\033[96m",
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "reset": "\033[0m",
    }

    def format(self, record):
        # Add the b10-transfer prefix to the message
        original_msg = record.getMessage()

        # Determine color based on log level and message content
        color = self._get_message_color(record, original_msg)

        # Format the message with color and prefix
        colored_msg = f"{self.COLORS[color]}[b10-transfer log] {original_msg}{self.COLORS['reset']}"

        # Temporarily replace the message for formatting
        record.msg = colored_msg
        record.args = ()

        # Use the parent formatter
        formatted = super().format(record)

        return formatted

    def _get_message_color(self, record, message: str) -> str:
        """Determine the appropriate color for the log message."""
        # Red for errors and failures
        if record.levelno >= logging.ERROR:
            return "red"

        # Red for warning messages that indicate failures
        if record.levelno == logging.WARNING and any(
            keyword in message.lower()
            for keyword in ["failed", "error", "interrupted", "cancelled", "abort"]
        ):
            return "red"

        # Green for success messages
        if any(
            keyword in message.lower()
            for keyword in [
                "completed successfully",
                "success",
                "complete",
                "finished",
                "saved",
                "loaded",
                "extracted",
                "compressed",
                "transferred",
                "cleared successfully",
            ]
        ):
            return "green"

        # Default to cyan
        return "cyan"


def get_b10_logger(name: str) -> logging.Logger:
    """Get a logger configured with b10-transfer colored formatting.

    Args:
        name: The logger name (typically __name__)

    Returns:
        Logger configured with colored b10-transfer formatting
    """
    logger = logging.getLogger(name)

    # Only add handler if it doesn't already exist
    if not any(
        isinstance(h, logging.StreamHandler)
        and isinstance(h.formatter, ColoredFormatter)
        for h in logger.handlers
    ):
        # Create handler with colored formatter
        handler = logging.StreamHandler()
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        # Prevent duplicate messages from parent loggers
        logger.propagate = False

    return logger


def log_success(logger: logging.Logger, message: str):
    """Log a success message that will be colored green."""
    logger.info(message)


def log_failure(logger: logging.Logger, message: str, level: int = logging.ERROR):
    """Log a failure message that will be colored red."""
    logger.log(level, message)


def log_info(logger: logging.Logger, message: str):
    """Log an info message that will be colored cyan."""
    logger.info(message)
