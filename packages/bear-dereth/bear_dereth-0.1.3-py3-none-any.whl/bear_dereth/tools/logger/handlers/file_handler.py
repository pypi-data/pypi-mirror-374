"""File handler implementation for BearLogger."""

from __future__ import annotations

from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, ClassVar

from rich.console import Console

from bear_dereth.constants.enums.log_level import LogLevel
from bear_dereth.tools.di._wiring import Provide, Provider, inject
from bear_dereth.tools.general.textio_utility import NULL_FILE
from bear_dereth.tools.logger.config import ConsoleOptions, Container, LoggerConfig
from bear_dereth.tools.logger.protocols.handler import Handler

if TYPE_CHECKING:
    from collections.abc import Callable


class FileHandler(Handler):
    """A handler that outputs messages to a file using Rich Console."""

    default_mode_attr: ClassVar[str] = "log"
    alt_mode_attr: ClassVar[str] = "log"

    @inject
    def __init__(
        self,
        *,
        name: str | None = None,
        file_path: str | Path | None = None,
        file_mode: str | None = None,
        encoding: str | None = None,
        config: LoggerConfig = Provide[Container.config],
        level: LogLevel | str | int = LogLevel.DEBUG,
        console_options: ConsoleOptions = Provide[Container.console_options],
        error_callback: Callable[..., Any] = Provide[Container.error_callback],
        root_level: Callable[[], LogLevel] = Provide[Container.root_level],
    ) -> None:
        """Initialize the FileHandler.

        Args:
            name: Optional name for the handler
            file_path: Path to the log file (as string or Path). If None, uses config value.
            file_mode: File open mode ('a' for append, 'w' for write). If None, uses config value.
            encoding: File encoding. If None, uses config value.
            level: Minimum logging level for this handler. If None, uses root logger level.
        """
        super().__init__()
        self.name: str | None = name
        self.config: LoggerConfig = config
        self.error_callback: Callable[..., Any] = error_callback
        self.get_level: Callable[..., LogLevel] = root_level
        self.level: LogLevel = LogLevel.get(level, default=self.get_level())
        self.file_path: Path = Path(file_path) if file_path else config.file.path()
        self.file_mode: str = file_mode if file_mode else config.file.mode
        self.encoding: str = encoding if encoding else config.file.encoding
        self.console_options: ConsoleOptions = console_options.model_copy()
        self.file = NULL_FILE
        if isinstance(self.console_options, Provider):  # TODO: We will remove this once I am more confident in DI
            print("Something went wrong with DI for console_options in FileHandler")
            return
        self.on_init()

    def on_init(self) -> None:
        """Hook for additional initialization if needed."""
        self.console_options.markup = False  # Disable markup for file output
        self.console_options.highlight = False  # Disable syntax highlighting for file output
        self.force_terminal = False  # Disable terminal features for file output
        self.file = self.open()
        self.caller = Console(file=self.file, **self.console_options.model_dump(exclude_none=True))

    def open(self) -> IO[Any]:
        """Open the file if it's not already open."""
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if self.file is NULL_FILE:
            file = self.file_path.open(self.file_mode, encoding=self.encoding)
            if hasattr(self, "caller") and hasattr(self.caller, "file"):
                self.caller.file = file
            return file
        return self.file if self.file is not None else NULL_FILE

    def emit(self, msg: object, style: str, level: LogLevel, **kwargs) -> None:  # noqa: ARG002
        """Emit a message to the file with the given style.

        Args:
            msg: The message to emit
            style: Rich style name to apply (may be stripped for plain text)
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments for Rich formatting
        """
        if self.caller and self.should_emit(level):
            try:
                self.output_func()(msg, **kwargs)
                self.file.flush() if self.file and not self.file.closed else None
            except Exception as e:
                print(f"FileHandler emit error: {e}")

    def __repr__(self) -> str:
        """String representation of the handler."""
        return f"FileHandler(file_path='{self.file_path}', level={self.level})"
