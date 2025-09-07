"""Grouping mixin for Collection class."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from ..collection import Collection

T = TypeVar("T")


class GroupingMixin[T]:
    """Mixin providing grouping methods."""

    def group_by(
        self, key: str | Callable[[T], Any] | None = None
    ) -> dict[Any, "Collection[T]"]:
        """
        Group the collection's items by a given key or callback function.

        Args:
            key: Either a string representing an attribute/key to group by,
                 or a callable that takes an item and returns the grouping key.
                 If None, groups by the item itself.

        Returns:
            A dictionary where keys are the grouping values and values are Collection
            instances containing the grouped items.

        Examples:
            # Group by attribute
            users.group_by('department')

            # Group by callback function
            users.group_by(lambda user: user.age // 10 * 10)  # Group by age decade

            # Group by item itself
            numbers.group_by()  # Groups identical numbers together
        """
        from ..collection import Collection

        if not self._items:
            return {}

        grouped = {}

        for item in self._items:
            if key is None:
                # Group by the item itself
                group_key = item
            elif isinstance(key, str):
                # Group by attribute/key (for dictionaries or objects)
                if isinstance(item, dict):
                    group_key = item.get(key)
                else:
                    group_key = getattr(item, key, None)
            elif callable(key):
                # Group by callback function
                group_key = key(item)
            else:
                raise ValueError("Key must be a string, callable, or None")

            # Convert key to hashable type for dictionary keys
            if isinstance(group_key, list | dict | set):
                group_key = str(group_key)

            if group_key not in grouped:
                grouped[group_key] = Collection()

            grouped[group_key].append(item)

        return grouped

    def chunk(self, size: int) -> list["Collection[T]"]:
        """
        Split the collection into smaller collections of the specified size.

        Args:
            size: The size of each chunk. Must be a positive integer.

        Returns:
            A list of Collection objects, each containing up to 'size' elements.
            The last chunk may contain fewer elements if the total number of elements
            is not evenly divisible by the chunk size.

        Raises:
            ValueError: If size is not a positive integer.
        """
        from ..collection import Collection

        if not isinstance(size, int) or size <= 0:
            raise ValueError("Chunk size must be a positive integer")

        if not self._items:
            return []

        chunks = []
        for i in range(0, len(self._items), size):
            chunk_items = self._items[i : i + size]
            chunks.append(Collection(chunk_items))

        return chunks
