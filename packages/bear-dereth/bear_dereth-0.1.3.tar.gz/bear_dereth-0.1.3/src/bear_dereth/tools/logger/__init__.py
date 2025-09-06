"""A module providing a Rich-based printer for colorful console output."""

from .config import CustomTheme, LoggerConfig, get_default_config
from .rich_printer import BearLogger

__all__ = ["BearLogger", "CustomTheme", "LoggerConfig", "get_default_config"]
