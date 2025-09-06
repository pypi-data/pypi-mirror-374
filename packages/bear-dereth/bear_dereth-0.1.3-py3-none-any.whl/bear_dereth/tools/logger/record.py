"""Logger record definition."""

from __future__ import annotations

from typing import Any, Self

from pydantic import Field

from bear_dereth.constants.enums.log_level import LogLevel
from bear_dereth.tools.general.freezing import FrozenModel


class LoggerRecord(FrozenModel):
    """A message container for queue processing."""

    msg: object = ""
    style: str = Field(default="")
    level: LogLevel = Field(default=LogLevel.DEBUG)
    args: tuple[Any, ...] | None = Field(default=None, repr=False)
    kwargs: dict[str, Any] | None = Field(default=None, repr=False)

    @classmethod
    def create(
        cls,
        msg: object,
        style: str = "",
        level: LogLevel = LogLevel.DEBUG,
        *args: Any,
        **kwargs: Any,
    ) -> Self:
        """Create a new QueueMessage instance."""
        return cls(msg=msg, style=style, level=level, args=args, kwargs=kwargs)
