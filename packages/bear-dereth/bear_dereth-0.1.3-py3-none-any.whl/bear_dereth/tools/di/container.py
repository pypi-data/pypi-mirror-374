"""Files to handle conditional imports of dependency injector container."""

from importlib.util import find_spec

_HAS_DEPENDENCY_INJECTOR: bool = find_spec("dependency_injector") is not None


if _HAS_DEPENDENCY_INJECTOR:
    from dependency_injector.containers import DeclarativeContainer  # type: ignore[import]

else:
    from bear_dereth.tools.di._container import DeclarativeContainer


__all__ = ["DeclarativeContainer"]
