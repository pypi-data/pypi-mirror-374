"""Navigation mixin for Collection class."""

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class NavigationMixin[T]:
    """Mixin providing navigation methods."""

    def after(self, target: T | Callable[[T], bool]) -> T | None:
        """
        Get the element that comes after the first occurrence of the target element or predicate match.

        Args:
            target: Either an element to search for, or a callable that takes an item and returns a boolean.
                   If an element is provided, searches for the first occurrence of that element.
                   If a callable is provided, searches for the first element that satisfies the predicate.

        Returns:
            The element that comes after the matched element, or None if no match is found or if the match
            is the last element in the collection.
        """
        if not self._items:
            return None

        # Handle case where target is a callable (predicate)
        if callable(target):
            predicate = target
            for i, item in enumerate(self._items):
                if predicate(item):
                    # Check if there's a next element
                    if i + 1 < len(self._items):
                        return self._items[i + 1]
                    return None
            return None

        # Handle case where target is an element
        try:
            index = self._items.index(target)
            # Check if there's a next element
            if index + 1 < len(self._items):
                return self._items[index + 1]
            return None
        except ValueError:
            # Element not found
            return None

    def before(self, target: T | Callable[[T], bool]) -> T | None:
        """
        Get the element that comes before the first occurrence of the target element or predicate match.

        Args:
            target: Either an element to search for, or a callable that takes an item and returns a boolean.
                   If an element is provided, searches for the first occurrence of that element.
                   If a callable is provided, searches for the first element that satisfies the predicate.

        Returns:
            The element that comes before the matched element, or None if no match is found or if the match
            is the first element in the collection.
        """
        if not self._items:
            return None

        # Handle case where target is a callable (predicate)
        if callable(target):
            predicate = target
            for i, item in enumerate(self._items):
                if predicate(item):
                    # Check if there's a previous element
                    if i > 0:
                        return self._items[i - 1]
                    return None
            return None

        # Handle case where target is an element
        try:
            index = self._items.index(target)
            # Check if there's a previous element
            if index > 0:
                return self._items[index - 1]
            return None
        except ValueError:
            # Element not found
            return None
