"""Logger configuration and theming using Pydantic and Rich."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING, Any, Literal, Self, TypeGuard

from bear_epoch_time import EpochTimestamp
from bear_epoch_time.constants.date_related import TIME_FORMAT_WITH_SECONDS
from pydantic import BaseModel, Field, model_validator
from rich._log_render import FormatTimeCallable
from rich.emoji import EmojiVariant
from rich.style import Style, StyleType
from rich.text import Text
from rich.theme import Theme

from bear_dereth.config.config_manager import ConfigManager
from bear_dereth.models.type_fields import LogLevelModel, PathModel
from bear_dereth.tools.di import DeclarativeContainer, Provide

if TYPE_CHECKING:
    from bear_dereth.constants.enums.log_level import LogLevel

type HighlighterType = Callable[[str], Text]


class LoggerTheme(BaseModel):
    """A Pydantic model representing a theme for logging."""

    info: str = "bold blue"
    warning: str = "bold yellow"
    error: str = "bold red"
    debug: str = "bold magenta"
    success: str = "bold green"
    failure: str = "bold red"
    exception: str = "underline bold red"

    model_config = {"extra": "forbid", "frozen": True}


class FileConfig(BaseModel):
    """A Pydantic model representing a file handler configuration."""

    disable: bool = True
    max_size: int = 10 * 1024 * 1024  # 10 MB
    path: PathModel = PathModel().set(Path("logs/app.log"))
    mode: str = "a"
    encoding: str = "utf-8"
    overrides: dict[str, Any] = Field(default_factory=dict)
    respect_handler_level: bool = True

    model_config = {"extra": "forbid", "frozen": True}


class QueueConfig(BaseModel):
    """A Pydantic model representing a queue listener configuration."""

    disable: bool = True
    max_queue_size: int = 1000
    worker_count: int = 2
    flush_interval: float = 0.5  # seconds
    queue: Queue = Field(default_factory=Queue, exclude=True)
    respect_handler_level: bool = True

    model_config = {"extra": "forbid", "arbitrary_types_allowed": True, "frozen": True}


class ConsoleHandlerConfig(BaseModel):
    """A Pydantic model representing a console handler configuration."""

    disable: bool = False
    overrides: dict[str, Any] = Field(default_factory=dict)
    respect_handler_level: bool = True


class RootLoggerConfig(BaseModel):
    """A Pydantic model representing the root logger configuration."""

    disable: bool = False
    level: LogLevelModel = LogLevelModel().set("DEBUG")
    overrides: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid", "frozen": True}


class LoggerConfig(BaseModel):
    """A Pydantic model representing the logger configuration."""

    root: RootLoggerConfig = RootLoggerConfig()
    console: ConsoleHandlerConfig = ConsoleHandlerConfig()
    file: FileConfig = FileConfig()
    queue: QueueConfig = QueueConfig()
    theme: LoggerTheme = LoggerTheme()

    model_config = {"extra": "forbid", "arbitrary_types_allowed": True}


def get_default_config() -> LoggerConfig:
    """Get the default logger configuration."""
    config_manager: ConfigManager[LoggerConfig] = ConfigManager(LoggerConfig, program_name="logger", env="prod")
    return config_manager.config


class CustomTheme(Theme):
    """A Rich Theme subclass that can be created from a ConfigManager."""

    @classmethod
    def from_config(cls, config: LoggerConfig) -> CustomTheme:
        """Create a CustomTheme from a ConfigManager."""
        return cls(styles=config.theme.model_dump())


def get_current_time() -> float:
    """Get the current time as an integer timestamp."""
    return EpochTimestamp.now()


def get_datetime() -> datetime:
    """Get the current datetime with local timezone if available."""
    local_tz = datetime.now().astimezone().tzinfo
    dt: datetime = EpochTimestamp.now().to_datetime
    return dt.astimezone(local_tz) if local_tz else dt


class ConsoleOptions(BaseModel):
    """A Pydantic model representing options for a Rich Console."""

    color_system: Literal["auto", "standard", "256", "truecolor", "windows"] = "auto"
    force_terminal: bool | None = None
    force_jupyter: bool | None = None
    force_interactive: bool | None = None
    soft_wrap: bool = False
    theme: Theme | CustomTheme | None = CustomTheme()
    no_theme: bool = Field(default=False, exclude=True)
    stderr: bool = False
    quiet: bool = False
    width: int | None = None
    height: int | None = None
    style: StyleType | Style | None = None
    no_color: bool | None = None
    tab_size: int = 8
    record: bool = False
    markup: bool = True
    emoji: bool = True
    emoji_variant: EmojiVariant | None = None
    highlight: bool = True
    log_time: bool = True
    log_path: bool = True
    log_time_format: str | FormatTimeCallable = f"[{TIME_FORMAT_WITH_SECONDS}]"
    highlighter: HighlighterType | None = None
    safe_box: bool = True
    get_datetime: Callable[[], datetime] | None = None
    get_time: Callable[[], float] | None = None

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def set_default_theme(self) -> Self:
        """Set the default theme if not provided."""
        if isinstance(self.theme, Theme):
            return self
        if self.theme is None and self.no_theme:
            return self
        self.theme = CustomTheme.from_config(get_default_config())
        return self

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        """Override model_dump to exclude None values by default."""
        if "exclude_none" not in kwargs:
            kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    def has_theme(self, theme: Theme | CustomTheme | None) -> TypeGuard[Theme | CustomTheme]:
        """Check if a theme is set and use a TypeGuard for type checking."""
        return theme is not None


class Container(DeclarativeContainer):
    """Dependency injection container for logger components."""

    error_callback: Callable[[Exception], None]
    root_level: Callable[..., LogLevel]
    config: LoggerConfig = get_default_config()
    custom_theme: CustomTheme = CustomTheme.from_config(config)
    console_options: ConsoleOptions = ConsoleOptions(theme=custom_theme)
    queue: Queue = config.queue.queue


container = Container()
Provide.set_container(container)
# ruff: noqa: TC002
