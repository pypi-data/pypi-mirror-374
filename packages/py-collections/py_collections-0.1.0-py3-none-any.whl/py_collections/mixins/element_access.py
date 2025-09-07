"""Element access mixin for Collection class."""

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class ItemNotFoundException(Exception):
    """Exception raised when an item is not found in the collection."""


class ElementAccessMixin[T]:
    """Mixin providing element access methods."""

    def first(self, predicate: Callable[[T], bool] | None = None) -> T | None:
        """
        Get the first element in the collection.

        Args:
            predicate: Optional callable that takes an item and returns a boolean.
                      If provided, returns the first element that satisfies the predicate.
                      If None, returns the first element in the collection.

        Returns:
            The first element that satisfies the predicate, or the first element if no predicate is provided.
            Returns None if the collection is empty or no element satisfies the predicate.
        """
        index = self._find_first_index(predicate)
        return self._items[index] if index is not None else None

    def exists(self, predicate: Callable[[T], bool] | None = None) -> bool:
        """
        Check if an element exists in the collection.

        Args:
            predicate: Optional callable that takes an item and returns a boolean.
                      If provided, checks if any element satisfies the predicate.
                      If None, checks if the collection is not empty.

        Returns:
            True if an element exists that satisfies the predicate (or if collection is not empty when no predicate),
            False otherwise.
        """
        return self._find_first_index(predicate) is not None

    def first_or_raise(self, predicate: Callable[[T], bool] | None = None) -> T:
        """
        Get the first element in the collection or raise ItemNotFoundException if not found.

        Args:
            predicate: Optional callable that takes an item and returns a boolean.
                      If provided, returns the first element that satisfies the predicate.
                      If None, returns the first element in the collection.

        Returns:
            The first element that satisfies the predicate, or the first element if no predicate is provided.

        Raises:
            ItemNotFoundException: If the collection is empty or no element satisfies the predicate.
        """
        index = self._find_first_index(predicate)
        if index is None:
            if not self._items:
                raise ItemNotFoundException(
                    "Cannot get first element from empty collection"
                )
            else:
                raise ItemNotFoundException("No element satisfies the predicate")
        return self._items[index]

    def last(self) -> T:
        """
        Get the last element in the collection.

        Returns:
            The last element in the collection.

        Raises:
            IndexError: If the collection is empty.
        """
        if not self._items:
            raise IndexError("Cannot get last element from empty collection")
        return self._items[-1]

    def _find_first_index(
        self, predicate: Callable[[T], bool] | None = None
    ) -> int | None:
        """
        Find the index of the first element that satisfies the predicate.

        Args:
            predicate: Optional callable that takes an item and returns a boolean.
                      If None, returns 0 (first element).

        Returns:
            Index of the first matching element, or None if not found.
        """
        if not self._items:
            return None

        if predicate is None:
            return 0

        for i, item in enumerate(self._items):
            if predicate(item):
                return i

        return None
