"""Logger-based message handler for API/service output."""

import logging
from typing import Any, Optional

from dooservice.shared.interfaces.message_handler import MessageHandler


class LoggerMessageHandler(MessageHandler):
    """Message handler that outputs to Python logger for API/service use."""

    def __init__(
        self, logger: Optional[logging.Logger] = None, name: Optional[str] = None
    ):
        """Initialize with optional logger instance or create new one."""
        if logger:
            self._logger = logger
        elif name:
            self._logger = logging.getLogger(name)
        else:
            self._logger = logging.getLogger(__name__)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message."""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log info message."""
        self._logger.info(message, *args, **kwargs)

    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log success message as info with SUCCESS prefix."""
        formatted_message = f"SUCCESS: {message}"
        self._logger.info(formatted_message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message."""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log error message."""
        self._logger.error(message, *args, **kwargs)

    def progress(
        self, message: str, completed: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Log progress message."""
        if completed:
            formatted_message = f"COMPLETED: {message}"
            self._logger.info(formatted_message, *args, **kwargs)
        else:
            formatted_message = f"PROGRESS: {message}"
            self._logger.info(formatted_message, *args, **kwargs)

    def progress_update(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Update progress message (same as completed progress for logger)."""
        formatted_message = f"COMPLETED: {message}"
        self._logger.info(formatted_message, *args, **kwargs)
