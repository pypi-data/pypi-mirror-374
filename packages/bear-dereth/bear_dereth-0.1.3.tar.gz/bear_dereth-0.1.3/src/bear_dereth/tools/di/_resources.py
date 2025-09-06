from __future__ import annotations

from abc import ABCMeta, abstractmethod
from threading import RLock
from typing import TYPE_CHECKING, Any, ClassVar, Self

from singleton_base.singleton_base_new import SingletonBase

if TYPE_CHECKING:
    from collections.abc import Callable


class Resource[T](metaclass=ABCMeta):
    __slots__: ClassVar[tuple[str, ...]] = ("args", "kwargs", "obj")

    obj: T | None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs
        self.obj = None

    @abstractmethod
    def init(self, *args: Any, **kwargs: Any) -> T | None: ...

    def shutdown(self, resource: T | None) -> None: ...  # noqa: B027

    def __enter__(self) -> T | None:
        self.obj = obj = self.init(*self.args, **self.kwargs)
        return obj

    def __exit__(self, *exc_info: object) -> None:
        self.shutdown(self.obj)
        self.obj = None


class Singleton[T](SingletonBase):
    """A base class for singleton classes"""

    __slots__: tuple = ("_args", "_constructor", "_instance", "_kwargs")

    @classmethod
    def get_lock(cls) -> RLock:
        if not hasattr(cls, "_lock"):
            cls._lock = RLock()
        return cls._lock

    def __init__(self, ctor: type[T] | Callable[..., T], /, *args, **kwargs) -> None:
        self._constructor: type[T] | Callable[..., T] = ctor
        self._instance: T | None = None
        self._args: tuple[Any, ...] = args
        self._kwargs: dict[str, Any] = kwargs

    @classmethod
    def from_instance(cls, value: T) -> Singleton[T]:
        obj: Self = cls.__new__(cls)
        obj._constructor = lambda: value
        obj._args = ()
        obj._kwargs = {}
        obj._instance = value
        return obj

    def get(self) -> T:
        if self._instance is not None:
            return self._instance
        with self.get_lock():
            if self._instance is None:
                self._instance = self._constructor(*self._args, **self._kwargs)
            return self._instance
