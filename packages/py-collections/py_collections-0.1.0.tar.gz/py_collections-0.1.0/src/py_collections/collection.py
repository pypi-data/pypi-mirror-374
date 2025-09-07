"""Main Collection class that combines all mixins."""

from typing import TypeVar

from .base_collection import BaseCollection
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
    BaseCollection[T],
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

    pass  # All functionality is inherited from BaseCollection and mixins
