"""Click-based message handler for console output."""

from typing import Any

import click

from dooservice.shared.interfaces.message_handler import MessageHandler


class ConsoleMessageHandler(MessageHandler):
    """Message handler that outputs to console using Click."""

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message with dim styling."""
        formatted_message = message % args if args else message
        click.secho(formatted_message, dim=True)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log info message with default styling."""
        formatted_message = message % args if args else message
        click.secho(formatted_message)

    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log success message with green styling."""
        formatted_message = message % args if args else message
        click.secho(formatted_message, fg="green")

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message with yellow styling."""
        formatted_message = message % args if args else message
        click.secho(formatted_message, fg="yellow")

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log error message with red styling."""
        formatted_message = message % args if args else message
        click.secho(formatted_message, fg="red")

    def progress(
        self, message: str, completed: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        """Show progress message with appropriate icon."""
        formatted_message = message % args if args else message

        if completed:
            # Success checkmark for completed tasks
            click.secho(f"✓ {formatted_message}", fg="green")
        else:
            # Progress indicator for ongoing tasks
            click.secho(f"□ {formatted_message}", dim=True)

    def progress_update(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Update progress message (overwrite previous line)."""
        formatted_message = message % args if args else message
        click.secho(f"\r✓ {formatted_message}", fg="green")
