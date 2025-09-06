"""BasePrinter protocol definition."""

from typing import IO, Any, Protocol, TextIO

from bear_dereth.constants.enums.log_level import LogLevel
from bear_dereth.tools.logger.config import CustomTheme, LoggerConfig
from bear_dereth.tools.logger.protocols.handler import Handler
from bear_dereth.tools.logger.protocols.handler_manager import BaseHandlerManager


class BasePrinter[T: TextIO | IO](BaseHandlerManager, Protocol):
    """A protocol for a base printer with config, theme, and user API."""

    name: str | None
    config: LoggerConfig
    level: LogLevel
    theme: CustomTheme
    handlers: list[Handler[Any]]

    def __init__(
        self,
        name: str | None = None,
        config: LoggerConfig | None = None,
        custom_theme: CustomTheme | None = None,
        file: T | None = None,
        level: int | str | LogLevel = LogLevel.DEBUG,
    ) -> None:
        """A constructor for the BasePrinter protocol."""

    def get_level(self) -> LogLevel:
        """Get the current logging level."""
        return self.level

    def set_level(self, level: str | int | LogLevel) -> None:
        """Set the current logging level."""
        self.level = LogLevel.get(level, self.level)

    def on_error_callback(self, name: str, error: Exception) -> None:
        """A method to handle errors from handlers."""

    def print(self, msg: object, style: str, **kwargs) -> None:
        """A method to print a message with a specific style directly to the console."""

    def log(self, msg: object, *args, **kwargs) -> None:
        """A method to log a message via console.log()."""
