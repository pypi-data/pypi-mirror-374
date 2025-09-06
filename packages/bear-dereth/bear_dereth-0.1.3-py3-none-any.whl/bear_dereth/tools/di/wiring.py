"""Dependency injection wiring tools."""

from importlib.util import find_spec

_HAS_DEPENDENCY_INJECTOR: bool = find_spec("dependency_injector") is not None


if _HAS_DEPENDENCY_INJECTOR:
    from dependency_injector.wiring import Provide, inject  # type: ignore[import]

else:
    from bear_dereth.tools.di._wiring import Provide, inject


__all__ = ["Provide", "inject"]
