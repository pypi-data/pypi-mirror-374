"""A simple dependency injection container with metaclass magic."""

from __future__ import annotations

from inspect import isclass
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple, TypedDict, TypeIs

from bear_dereth.tools.di._resources import Resource
from bear_dereth.tools.di._wiring import Provide
from bear_dereth.tools.general.freezing import FrozenDict, freeze
from bear_dereth.tools.general.priority_queue import PriorityQueue

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType


class DeclarativeContainerMeta(type):
    """Metaclass that captures service declarations and makes the injection magic work."""

    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> DeclarativeContainerMeta:
        """Create a new container class with provider magic."""
        Provide.set_container(mcs)
        annotations: dict[str, Any] = namespace.get("__annotations__", {})
        service_types: dict[str, Any] = {}
        for service_name, service_type in annotations.items():
            if not service_name.startswith("_"):
                service_types[service_name] = service_type
        namespace["_service_types"] = service_types
        if "_services" not in namespace:
            namespace["_services"] = {}
        if "_service_metadata" not in namespace:
            namespace["_service_metadata"] = {}
        return super().__new__(mcs, name, bases, namespace)

    def __getattr__(cls, name: str) -> Any:
        """Return a Provide instance for any service name."""
        service_types: dict[str, Any] = getattr(cls, "_service_types", {})
        if name.lower() in service_types:
            return Provide(name.lower(), cls)
        raise AttributeError(f"'{cls.__name__}' has no attribute '{name}'")

    @property
    def get_all_shutdowns(cls) -> dict[str, Any]:
        """Return all services that have a shutdown method.

        This allows us to always know that these services have a valid shutdown method.

        Returns:
            dict[str, Any]: A dictionary of service names to service instances that have a shutdown method
            that are considered valid shutdown services.
        """
        if not hasattr(cls, "_services"):
            return {}
        data: dict[str, Any] = cls._services
        return {k: v for k, v in data.items() if hasattr(v, "shutdown") and callable(v.shutdown)}


class MetadataInfo(TypedDict):
    """Metadata information about a registered service."""

    type_name: str
    module: str
    is_class: bool
    id: int


class TearDownCallback(NamedTuple):
    """Information about a registered teardown callback."""

    priority: float
    name: str
    callback: Callable[[], None]


class DeclarativeContainer(metaclass=DeclarativeContainerMeta):
    """A simple service container for dependency injection."""

    _services: ClassVar[dict[str, Any]] = {}
    """The registered services in the container."""
    _service_types: ClassVar[dict[str, type]] = {}
    """The types of the registered services in the container."""
    _service_metadata: ClassVar[dict[str, FrozenDict]] = {}
    """The metadata of the registered services in the container as frozen dictionaries."""
    _teardown_callbacks: ClassVar[PriorityQueue[TearDownCallback]] = PriorityQueue()
    """A priority queue of teardown callbacks to be executed during shutdown."""
    _resources: ClassVar[list[tuple[str, Resource[Any]]]] = []
    """A list of resources that have been started and need to be shut down."""

    def __name__(self) -> str:
        """Return the name of the container class."""
        return self.__class__.__name__

    def __hash__(self) -> int:
        """Make the container class hashable."""
        return hash(self._service_metadata)

    @staticmethod
    def _get_metadata(instance: Any) -> FrozenDict:
        """Get metadata about a service instance or class.

        Args:
            instance (Any): The service instance or class to get metadata for.

        Returns:
            FrozenDict: A frozen dictionary containing metadata about the service.
        """
        metadata: MetadataInfo = {
            "type_name": "",
            "module": "",
            "is_class": False,
            "id": 0,
        }
        is_class: TypeIs[type[Any]] = isclass(instance)
        metadata["id"] = id(instance)
        metadata["type_name"] = instance.__name__ if is_class else type(instance).__name__
        metadata["module"] = (
            getattr(instance, "__module__", "") if is_class else getattr(type(instance), "__module__", "")
        )
        metadata["is_class"] = is_class
        return freeze(metadata)

    @classmethod
    def register(cls, name: str, instance: Any) -> None:
        """Register a service instance with a name and optional metadata."""
        cls._services[name.lower()] = instance
        cls._service_metadata[name.lower()] = cls._get_metadata(instance)

    @classmethod
    def get(cls, name: str, expected_type: type | None = None) -> Any | None:
        if name.lower() in cls._services:
            return cls._services[name.lower()]
        if hasattr(cls, name):
            resource: Any = getattr(cls, name)
            if expected_type and not isinstance(resource, expected_type):
                return None
            if isclass(resource):
                return resource()
            return resource
        return None

    @classmethod
    def get_all(cls) -> dict[str, Any]:
        """Get all registered services."""
        return cls._services.copy()

    @classmethod
    def get_all_types(cls) -> dict[str, Any]:
        """Get all registered service types."""
        return cls._service_types.copy()

    @classmethod
    def get_all_metadata(cls) -> FrozenDict:
        """Get all registered service metadata as a frozen dictionary.

        This is the representation that is hashable and can be used for caching purposes.

        Returns:
            FrozenDict: A frozen dictionary of all registered service metadata.
        """
        return freeze(cls._service_metadata.copy())

    @classmethod
    def has(cls, name: str) -> bool:
        """Check if a service is registered."""
        return name.lower() in cls._services or hasattr(cls, name)

    @classmethod
    def override(cls, name: str, instance: Any) -> None:
        """Add an instance to the container using its class name as the key."""
        cls._services[name.lower()] = instance
        cls._service_metadata[name.lower()] = cls._get_metadata(instance)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered services and metadata."""
        cls._services.clear()
        cls._service_metadata.clear()
        cls._resources.clear()

    @classmethod
    def start(cls) -> None:
        """Start all registered resources."""
        for name, service in list(cls._services.items()):
            if isinstance(service, Resource):
                obj = service.__enter__()
                cls._resources.append((name, service))
                cls._services[name] = obj

    @classmethod
    def register_teardown(cls, name: str, callback: Callable[[], None], priority: float = float("inf")) -> None:
        """Register a callback to be executed during shutdown.

        Args:
            name (str): The name of the teardown callback.
            callback (Callable[[], None]): The callback function to be executed during shutdown.
            priority (float, optional): The priority of the callback. Lower values indicate higher priority.
                Defaults to float('inf') indicating lowest priority.

        Example:
            -------
            ```python
            class AppContainer(DeclarativeContainer):
                db: Database


            db = Database()
            AppContainer.register("db", db)
            AppContainer.register_teardown(lambda: db.close())
            AppContainer.shutdown()
        ```
        """
        if not callable(callback):
            return
        callback_info = TearDownCallback(priority=float(priority), name=name, callback=callback)
        cls._teardown_callbacks.put(callback_info)

    @classmethod
    def remove_teardown(cls, name: str) -> bool:
        """Remove a registered teardown callback by name.

        Args:
            name (str): The name of the teardown callback to remove.

        Returns:
            bool: True if the callback was found and removed, False otherwise.
        """
        return cls._teardown_callbacks.remove_element("name", name)

    @classmethod
    def shutdown(cls) -> None:
        """Shutdown services and execute registered teardown callbacks."""
        for service in cls.get_all_shutdowns.values():
            try:
                service.shutdown()
            except TypeError:
                arg: Any = getattr(service, "obj", service)
                service.shutdown(arg)

        while cls._teardown_callbacks:
            callback_info: TearDownCallback = cls._teardown_callbacks.get()

            callback_info.callback()  # Just let the error propagate

        while cls._resources:
            name, resource = cls._resources.pop()
            try:
                resource.__exit__(None, None, None)
            finally:
                cls._services[name] = resource

        cls.clear()
        cls._teardown_callbacks.clear()
        cls._resources.clear()

    @classmethod
    def __enter__(cls) -> type[DeclarativeContainer]:
        cls.start()
        return cls

    @classmethod
    def __exit__(
        cls,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        cls.shutdown()
