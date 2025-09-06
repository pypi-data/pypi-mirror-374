"""Message handler container for dependency injection."""

from typing import Optional

from dooservice.shared.infrastructure.logger_message_handler import LoggerMessageHandler
from dooservice.shared.interfaces.message_handler import MessageHandler


class MessageContainer:
    """Singleton container for message handler dependency injection."""

    _instance: Optional["MessageContainer"] = None
    _message_handler: Optional[MessageHandler] = None

    def __new__(cls) -> "MessageContainer":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_handler(self, handler: MessageHandler) -> None:
        """Set the global message handler."""
        self._message_handler = handler

    def get_handler(self) -> MessageHandler:
        """Get the current message handler or create default one."""
        if self._message_handler is None:
            self._message_handler = LoggerMessageHandler(name="dooservice")
        return self._message_handler

    def reset(self) -> None:
        """Reset the container (useful for testing)."""
        self._message_handler = None


# Global convenience functions
def set_message_handler(handler: MessageHandler) -> None:
    """Set the global message handler."""
    MessageContainer().set_handler(handler)


def get_message_handler() -> MessageHandler:
    """Get the current global message handler."""
    return MessageContainer().get_handler()
