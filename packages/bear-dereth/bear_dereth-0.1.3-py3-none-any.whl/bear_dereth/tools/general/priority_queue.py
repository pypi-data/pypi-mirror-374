"""A simple priority queue implementation using a heap."""

from collections.abc import Iterator
from heapq import heapify, heappop, heappush, nsmallest
from typing import Any


class PriorityQueue[QueueType: Any]:
    """A simple priority queue implementation using a heap."""

    def __init__(self) -> None:
        """A simple priority queue implementation using a heap."""
        self._elements: list[QueueType] = []

    def put(self, item: QueueType) -> None:
        """Add an item to the queue."""
        heappush(self._elements, item)

    def get(self) -> QueueType:
        """Remove and return the highest priority item from the queue."""
        if self.empty():
            raise IndexError("get from empty priority queue")
        return heappop(self._elements)

    def peek(self) -> QueueType:
        """Return the highest priority item without removing it."""
        if self.empty():
            raise IndexError("peek from empty priority queue")
        return self._elements[0]

    def empty(self) -> bool:
        """Check if the queue is empty."""
        return not self._elements

    def clear(self) -> None:
        """Clear all items from the queue."""
        self._elements.clear()

    def sorted_items(self) -> Iterator[QueueType]:
        """Return items in priority order without modifying the queue."""
        return iter(nsmallest(len(self._elements), self._elements))

    def remove_element(self, key: str, value: Any) -> bool:
        """Remove an item from the queue based on a key-value pair.

        Args:
            key (str): The attribute name to match.
            value (Any): The value to match against the attribute.

        Returns:
            bool: True if an item was removed, False otherwise.
        """
        if self.empty():
            return False

        try:
            item_to_remove: QueueType = next(item for item in self._elements if getattr(item, key, None) == value)
            self._elements.remove(item_to_remove)
            heapify(self._elements)
            return True
        except StopIteration:
            return False
        except ValueError:
            return False

    @property
    def size(self) -> int:
        """Get the number of items in the queue."""
        return len(self._elements)

    def __len__(self) -> int:
        return len(self._elements)

    def __bool__(self) -> bool:
        return bool(self._elements)

    def __iter__(self) -> Iterator[QueueType]:
        """Iterate over items in priority order (destructive)."""
        while self._elements:
            yield heappop(self._elements)
