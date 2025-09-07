"""Base collection class that provides the core functionality."""

from typing import TypeVar

T = TypeVar("T")


class BaseCollection[T]:
    """
    Base collection class that wraps a list and provides core functionality.

    This class serves as the foundation for all collection types and provides
    the basic structure that mixins can build upon.
    """

    def __init__(self, items: list[T] | None = None):
        """
        Initialize the collection with items.

        Args:
            items: Optional list of items to initialize the collection with.
                   If not provided, an empty list will be used.
        """
        self._items = items.copy() if items is not None else []

    def __str__(self) -> str:
        """Return a string representation of the collection."""
        return f"{self.__class__.__name__}({self._items})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the collection."""
        return f"{self.__class__.__name__}({self._items})"

    def __len__(self) -> int:
        """Return the number of items in the collection."""
        return len(self._items)

    def __iter__(self):
        """
        Return an iterator over the collection's items.

        Returns:
            An iterator that yields each item in the collection.
        """
        return iter(self._items)
