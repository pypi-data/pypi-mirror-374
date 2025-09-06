"""Message handler interface for different output modes."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class MessageLevel(Enum):
    """Message severity levels."""

    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class MessageHandler(ABC):
    """Abstract interface for handling messages across different output modes."""

    @abstractmethod
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message."""

    @abstractmethod
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log info message."""

    @abstractmethod
    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log success message."""

    @abstractmethod
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message."""

    @abstractmethod
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log error message."""

    @abstractmethod
    def progress(
        self, message: str, completed: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Show progress message (e.g., '□ Processing...' or '✓ Completed')."""

    def message(
        self, level: MessageLevel, message: str, *args: Any, **kwargs: Any
    ) -> None:
        """Generic message method that delegates to specific level methods."""
        level_methods = {
            MessageLevel.DEBUG: self.debug,
            MessageLevel.INFO: self.info,
            MessageLevel.SUCCESS: self.success,
            MessageLevel.WARNING: self.warning,
            MessageLevel.ERROR: self.error,
        }
        method = level_methods.get(level, self.info)
        method(message, *args, **kwargs)
