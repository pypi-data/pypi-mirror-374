from collections.abc import Callable, Iterator
from typing import Any, TypeVar

from .collection import Collection

T = TypeVar("T")


class CollectionMap[T]:
    """
    A specialized map that stores Collection instances as values.

    This class provides a convenient way to work with grouped data,
    ensuring all values are Collection instances and providing
    useful methods for working with grouped collections.

    Args:
        data: Optional dictionary to initialize the CollectionMap.
              Values should be either Collection instances or iterables
              that will be converted to Collection instances.
    """

    def __init__(self, data: dict[str, Collection[T] | list[T] | Any] | None = None):
        self._data: dict[str, Collection[T]] = {}

        if data is not None:
            for key, value in data.items():
                self[key] = value

    def __setitem__(self, key: str, value: Collection[T] | list[T] | Any) -> None:
        """
        Set a key-value pair, converting the value to a Collection if needed.

        Args:
            key: String key for the mapping
            value: Value to store. If not a Collection, will be converted to one.
        """
        if isinstance(value, Collection):
            self._data[key] = value
        elif isinstance(value, list | tuple):
            self._data[key] = Collection(list(value))
        else:
            # Convert single item to a collection
            self._data[key] = Collection([value])

    def __getitem__(self, key: str) -> Collection[T]:
        """
        Get a Collection by key.

        Args:
            key: String key to retrieve

        Returns:
            Collection instance for the given key

        Raises:
            KeyError: If the key doesn't exist
        """
        if key not in self._data:
            raise KeyError(f"Key '{key}' not found in CollectionMap")
        return self._data[key]

    def __delitem__(self, key: str) -> None:
        """
        Remove a key-value pair.

        Args:
            key: String key to remove
        """
        if key in self._data:
            del self._data[key]

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the CollectionMap."""
        return key in self._data

    def __len__(self) -> int:
        """Return the number of key-value pairs."""
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the keys."""
        return iter(self._data)

    def keys(self) -> list[str]:
        """Get all keys as a list."""
        return list(self._data.keys())

    def values(self) -> list[Collection[T]]:
        """Get all Collection values as a list."""
        return list(self._data.values())

    def items(self) -> list[tuple[str, Collection[T]]]:
        """Get all key-value pairs as a list of tuples."""
        return list(self._data.items())

    def get(self, key: str, default: Collection[T] | None = None) -> Collection[T]:
        """
        Get a Collection by key with optional default value.

        Args:
            key: String key to retrieve
            default: Default value to return if key doesn't exist.
                   If None, returns an empty Collection.

        Returns:
            Collection instance or default value
        """
        if default is None:
            return self._data.get(key, Collection())
        return self._data.get(key, default)

    def add(self, key: str, items: Collection[T] | list[T] | Any) -> None:
        """
        Add items to a Collection by key, creating the key if it doesn't exist.

        Args:
            key: String key to add items to
            items: Items to add. Can be a Collection, list, tuple, or single item.
                  If the key doesn't exist, creates a new Collection with these items.
                  If the key exists, extends the existing Collection with these items.
        """
        if key not in self._data:
            # Create new collection
            if isinstance(items, Collection):
                self._data[key] = items
            elif isinstance(items, list | tuple):
                self._data[key] = Collection(list(items))
            else:
                self._data[key] = Collection([items])
        # Extend existing collection
        elif isinstance(items, Collection):
            self._data[key]._items.extend(items.all())
        elif isinstance(items, list | tuple):
            self._data[key]._items.extend(items)
        else:
            self._data[key].append(items)

    def setdefault(
        self, key: str, default: Collection[T] | list[T] | Any = None
    ) -> Collection[T]:
        """
        Get a Collection by key, creating it with default value if it doesn't exist.

        Args:
            key: String key to retrieve or create
            default: Default value to use if key doesn't exist

        Returns:
            Collection instance for the given key
        """
        if key not in self._data:
            if default is None:
                self._data[key] = Collection()
            else:
                self[key] = default
        return self._data[key]

    def update(self, other: dict[str, Collection[T] | list[T] | Any]) -> None:
        """
        Update the CollectionMap with items from another dictionary.

        Args:
            other: Dictionary to update from
        """
        for key, value in other.items():
            self[key] = value

    def clear(self) -> None:
        """Remove all key-value pairs."""
        self._data.clear()

    def pop(
        self, key: str, default: Collection[T] | None = None
    ) -> Collection[T] | None:
        """
        Remove and return a Collection by key.

        Args:
            key: String key to remove
            default: Default value to return if key doesn't exist

        Returns:
            Removed Collection instance or default value
        """
        return self._data.pop(key, default)

    def popitem(self) -> tuple[str, Collection[T]]:
        """
        Remove and return a (key, Collection) pair.

        Returns:
            Tuple of (key, Collection)

        Raises:
            KeyError: If the CollectionMap is empty
        """
        if not self._data:
            raise KeyError("CollectionMap is empty")
        return self._data.popitem()

    def copy(self) -> "CollectionMap[T]":
        """Create a shallow copy of the CollectionMap."""
        result = CollectionMap()
        result._data = self._data.copy()
        return result

    def flatten(self) -> Collection[T]:
        """
        Flatten all Collections into a single Collection.

        Returns:
            A single Collection containing all items from all groups
        """
        result = Collection()
        for collection in self._data.values():
            result._items.extend(collection.all())
        return result

    def map(self, func: Callable[[Collection[T]], Any]) -> dict[str, Any]:
        """
        Apply a function to each Collection in the map.

        Args:
            func: Function to apply to each Collection

        Returns:
            Dictionary mapping keys to function results
        """
        return {key: func(collection) for key, collection in self._data.items()}

    def filter(
        self, predicate: Callable[[str, Collection[T]], bool]
    ) -> "CollectionMap[T]":
        """
        Filter the CollectionMap based on a predicate function.

        Args:
            predicate: Function that takes (key, collection) and returns boolean

        Returns:
            New CollectionMap containing only items that satisfy the predicate
        """
        result = CollectionMap()
        for key, collection in self._data.items():
            if predicate(key, collection):
                result[key] = collection
        return result

    def filter_by_size(
        self, min_size: int = 0, max_size: int | None = None
    ) -> "CollectionMap[T]":
        """
        Filter Collections based on their size.

        Args:
            min_size: Minimum size (inclusive)
            max_size: Maximum size (inclusive), None for no upper limit

        Returns:
            New CollectionMap containing only Collections within the size range
        """

        def size_predicate(key: str, collection: Collection[T]) -> bool:
            size = len(collection)
            if max_size is None:
                return size >= min_size
            return min_size <= size <= max_size

        return self.filter(size_predicate)

    def total_items(self) -> int:
        """
        Get the total number of items across all Collections.

        Returns:
            Total count of all items
        """
        return sum(len(collection) for collection in self._data.values())

    def largest_group(self) -> tuple[str, Collection[T]] | None:
        """
        Get the group with the most items.

        Returns:
            Tuple of (key, collection) for the largest group, or None if empty
        """
        if not self._data:
            return None

        largest_key = max(self._data.keys(), key=lambda k: len(self._data[k]))
        return largest_key, self._data[largest_key]

    def smallest_group(self) -> tuple[str, Collection[T]] | None:
        """
        Get the group with the fewest items.

        Returns:
            Tuple of (key, collection) for the smallest group, or None if empty
        """
        if not self._data:
            return None

        smallest_key = min(self._data.keys(), key=lambda k: len(self._data[k]))
        return smallest_key, self._data[smallest_key]

    def group_sizes(self) -> dict[str, int]:
        """
        Get the size of each group.

        Returns:
            Dictionary mapping keys to their Collection sizes
        """
        return {key: len(collection) for key, collection in self._data.items()}

    def __str__(self) -> str:
        """Return a string representation of the CollectionMap."""
        items = [f"'{key}': {collection}" for key, collection in self._data.items()]
        return f"CollectionMap({{{', '.join(items)}}})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the CollectionMap."""
        return self.__str__()
