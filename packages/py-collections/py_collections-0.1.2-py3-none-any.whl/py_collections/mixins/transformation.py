"""Transformation mixin for Collection class."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from ..collection import Collection

T = TypeVar("T")


class TransformationMixin[T]:
    """Mixin providing transformation methods."""

    def map(self, func: Callable[[T], Any]) -> "Collection[Any]":
        """
        Apply a function to every item in the collection and return a new collection with the results.

        Args:
            func: A callable that takes an item and returns a transformed value.

        Returns:
            A new Collection containing the transformed items.

        Examples:
            collection = Collection([1, 2, 3, 4, 5])
            collection.map(lambda x: x * 2).all()  # [2, 4, 6, 8, 10]
            collection.map(str).all()  # ['1', '2', '3', '4', '5']
            collection.map(lambda x: x ** 2).all()  # [1, 4, 9, 16, 25]
        """
        from ..collection import Collection

        mapped_items = [func(item) for item in self._items]
        return Collection(mapped_items)

    def pluck(self, key: str, value_key: str | None = None) -> "Collection[Any]":
        """
        Extract values from a collection of items based on a key or attribute.

        Args:
            key: The key or attribute to extract values from. Supports dot notation for nested access.
            value_key: Optional key to use as the value. If provided, returns a dictionary
                      with the original key as keys and value_key as values.

        Returns:
            A new Collection containing the extracted values.

        Examples:
            # Extract names from a collection of dictionaries
            users = Collection([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
            users.pluck("name").all()  # ["Alice", "Bob"]

            # Extract names with ages as values
            users.pluck("name", "age").all()  # [{"Alice": 25}, {"Bob": 30}]

            # Extract nested values using dot notation
            users = Collection([{"name": "Alice", "address": {"city": "NYC"}}, {"name": "Bob", "address": {"city": "LA"}}])
            users.pluck("address.city").all()  # ["NYC", "LA"]

            # Extract from objects with attributes
            class User:
                def __init__(self, name, age):
                    self.name = name
                    self.age = age
            users = Collection([User("Alice", 25), User("Bob", 30)])
            users.pluck("name").all()  # ["Alice", "Bob"]
        """
        from ..collection import Collection

        if not self._items:
            return Collection()

        def get_nested_value(obj, key_path: str):
            """Get nested value using dot notation."""
            keys = key_path.split(".")
            current = obj

            for k in keys:
                if isinstance(current, dict):
                    if k in current:
                        current = current[k]
                    else:
                        return None
                elif hasattr(current, k):
                    current = getattr(current, k)
                else:
                    return None

                if current is None:
                    return None

            return current

        plucked_items = []

        for item in self._items:
            key_value = get_nested_value(item, key)

            if value_key is None:
                plucked_items.append(key_value)
            else:
                value_value = get_nested_value(item, value_key)
                plucked_items.append({key_value: value_value})

        return Collection(plucked_items)

    def filter(self, predicate: Callable[[T], bool]) -> "Collection[T]":
        """
        Filter the collection based on a predicate function.

        Args:
            predicate: A callable that takes an item and returns a boolean.
                      Items that return True will be included in the filtered collection.

        Returns:
            A new Collection containing only the elements that satisfy the predicate.
        """
        from ..collection import Collection

        filtered_items = [item for item in self._items if predicate(item)]
        return Collection(filtered_items)

    def reverse(self) -> "Collection[T]":
        """
        Return a new collection with the items reversed in order.

        Returns:
            A new Collection containing the items in reverse order.
        """
        from ..collection import Collection

        reversed_items = self._items[::-1]
        return Collection(reversed_items)

    def clone(self) -> "Collection[T]":
        """
        Return a new collection with the same items.

        Returns:
            A new Collection containing the same items as the original.
        """
        from ..collection import Collection

        return Collection(self._items.copy())
