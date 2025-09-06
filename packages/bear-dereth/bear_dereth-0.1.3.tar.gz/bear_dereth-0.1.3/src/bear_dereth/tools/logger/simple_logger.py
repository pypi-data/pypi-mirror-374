"""Simple logger implementation with log levels and timestamped output."""

import traceback
from typing import TextIO

from bear_epoch_time import EpochTimestamp

from bear_dereth.constants.enums.log_level import LogLevel
from bear_dereth.tools.general.textio_utility import stderr


class SimpleLogger[T: TextIO]:
    """A simple logger that writes messages to stdout, stderr, or StringIO with a timestamp."""

    def __init__(self, level: str | int | LogLevel = "DEBUG", file: T | None = None) -> None:
        """Initialize the logger with a minimum log level and output file.

        Args:
            level (str | int | LogLevel): The minimum log level for messages to be logged.
            file (TextIO): The file-like object to write log messages to. Defaults to STDERR.
        """
        self.level: LogLevel = LogLevel.get(level, default=LogLevel.DEBUG)
        self.file: T | TextIO = file if file is not None else stderr()
        self.buffer: list[str] = []

    def set_file(self, file: T) -> None:
        """Set the output file for the logger."""
        self.file = file

    def print(self, msg: object, end: str = "\n") -> None:
        """Print the message to the specified file with an optional end character."""
        print(msg, end=end, file=self.file)

    def _log(self, level: LogLevel, msg: object, end: str = "\n", *args, **kwargs) -> None:
        timestamp: str = EpochTimestamp.now().to_string()
        try:
            self.buffer.append(f"[{timestamp}] {level.text}: {msg}")
            if args:
                self.buffer.append(" ".join(str(arg) for arg in args))
            if kwargs:
                for key, value in kwargs.items():
                    self.buffer.append(f"{key}={value}")
            self.print(f"{end}".join(self.buffer))
        except Exception as e:
            self.print(f"[{timestamp}] {level.value}: {msg} - Error: {e}")
        finally:
            self.buffer.clear()

    def log(self, level: LogLevel, msg: object, *args, **kwargs) -> None:
        """Log a message at the specified level."""
        if level.value >= self.level.value:
            self._log(level, msg, *args, **kwargs)

    def verbose(self, msg: object, *args, **kwargs) -> None:
        """Alias for debug level logging."""
        self.log(LogLevel.VERBOSE, msg, *args, **kwargs)

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        self.log(LogLevel.DEBUG, msg, *args, **kwargs)

    def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        self.log(LogLevel.INFO, msg, *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        self.log(LogLevel.WARNING, msg, *args, **kwargs)

    def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        self.log(LogLevel.ERROR, msg, *args, **kwargs)

    def success(self, msg: object, *args, **kwargs) -> None:
        """Log a success message."""
        self.log(LogLevel.SUCCESS, msg, *args, **kwargs)

    def failure(self, msg: object, *args, **kwargs) -> None:
        """Log a failure message."""
        self.log(LogLevel.FAILURE, msg, *args, **kwargs)

    def exception(self, msg: object, *args, exc_info: bool = True, **kwargs) -> None:
        """Log an exception message with optional exception info."""
        if exc_info:
            exc_msg = traceback.format_exc()
            msg = f"{msg}\n{exc_msg}"
        self.log(LogLevel.EXCEPTION, msg, *args, **kwargs)


__all__ = ["SimpleLogger"]

# # Example usage:
# if __name__ == "__main__":
#     logger: SimpleLogger[StringIO] = SimpleLogger(file=StringIO())
#     logger_two: SimpleLogger[NullFile] = SimpleLogger(level="INFO", file=NullFile())
#     logger.info(msg="This is an info message")
#     logger_two.info(msg="This is an info message")

#     value = logger.file
#     print(value.getvalue())  # Print the captured log messages from StringIO
#     # print(logger_two.file.getvalue())  # should throw a typing error since it is not a StringIO
