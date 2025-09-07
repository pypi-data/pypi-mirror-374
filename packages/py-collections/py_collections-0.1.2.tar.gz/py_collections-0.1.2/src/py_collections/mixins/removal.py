"""Removal mixin for Collection class."""

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class RemovalMixin[T]:
    """Mixin providing removal methods."""

    def remove(self, target: T | Callable[[T], bool]) -> None:
        """
        Remove all items that match the target element or predicate.

        Args:
            target: Either an element to remove, or a callable that takes an item and returns a boolean.
                   If an element is provided, removes all occurrences of that element.
                   If a callable is provided, removes all elements that satisfy the predicate.
        """
        if callable(target):
            predicate = target
            self._items[:] = [item for item in self._items if not predicate(item)]
        else:
            self._items[:] = [item for item in self._items if item != target]

    def remove_one(self, target: T | Callable[[T], bool]) -> None:
        """
        Remove the first occurrence of an item that matches the target element or predicate.

        Args:
            target: Either an element to remove, or a callable that takes an item and returns a boolean.
                   If an element is provided, removes the first occurrence of that element.
                   If a callable is provided, removes the first element that satisfies the predicate.
        """
        if not self._items:
            return

        if callable(target):
            predicate = target
            for i, item in enumerate(self._items):
                if predicate(item):
                    del self._items[i]
                    return
        else:
            try:
                self._items.remove(target)
            except ValueError:
                # Element not found, do nothing
                pass
