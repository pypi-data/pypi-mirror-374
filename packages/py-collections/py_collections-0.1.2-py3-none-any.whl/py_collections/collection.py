"""Main Collection class that combines all mixins."""

from typing import TypeVar

from .mixins import (
    BasicOperationsMixin,
    ElementAccessMixin,
    GroupingMixin,
    NavigationMixin,
    RemovalMixin,
    TransformationMixin,
    UtilityMixin,
)

T = TypeVar("T")


class Collection[T](
    BasicOperationsMixin[T],
    ElementAccessMixin[T],
    NavigationMixin[T],
    TransformationMixin[T],
    GroupingMixin[T],
    RemovalMixin[T],
    UtilityMixin[T],
):
    """
    A collection class that wraps a list and provides methods to manipulate it.

    This class combines functionality from multiple mixins:
    - BasicOperationsMixin: append, extend, all, len, iteration
    - ElementAccessMixin: first, last, exists, first_or_raise
    - NavigationMixin: after, before
    - TransformationMixin: map, pluck, filter, reverse, clone
    - GroupingMixin: group_by, chunk
    - RemovalMixin: remove, remove_one
    - UtilityMixin: take, dump_me, dump_me_and_die

    Args:
        items: Optional list of items to initialize the collection with.
               If not provided, an empty list will be used.
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
