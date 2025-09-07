#!/usr/bin/env python3
"""
Comprehensive example demonstrating all Collection methods together.
"""

import contextlib

from py_collections import Collection


def main():
    """Demonstrate all Collection functionality in a comprehensive example."""

    # 1. Initialize collections
    numbers = Collection([1, 2, 3, 4, 5])
    strings = Collection(["apple", "banana"])
    empty = Collection()

    # 2. Append operations
    numbers.append(6)
    numbers.append(7)
    strings.append("cherry")
    empty.append("first item")

    # 3. First, last, after, filter, first_or_raise, chunk, take, map, pluck, and dump_me operations

    # First with predicate examples

    # After examples

    # Before examples

    # Filter examples
    numbers.filter(lambda x: x % 2 == 0)
    strings.filter(lambda s: len(s) > 5)

    # Map examples
    numbers.map(lambda x: x * 2)  # Double each number
    strings.map(str.upper)  # Convert to uppercase
    numbers.map(str)  # Convert to strings

    # Pluck examples
    users = Collection([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
    users.pluck("name")  # Extract names
    users.pluck("name", "age")  # Create name-age pairs

    # Nested key examples
    nested_users = Collection(
        [
            {"name": "Alice", "address": {"city": "NYC"}},
            {"name": "Bob", "address": {"city": "LA"}},
        ]
    )
    nested_users.pluck("address.city")  # Extract nested cities
    nested_users.pluck("name", "address.city")  # Create name-city pairs

    # Take examples
    numbers.take(3)  # Take first 3 items
    numbers.take(-2)  # Take last 2 items
    strings.take(1)  # Take first item

    # First_or_raise examples

    # Chunk examples
    numbers.chunk(2)
    strings.chunk(1)

    # Dump_me example (commented out to avoid stopping execution)

    # 4. All items operations
    all_numbers = numbers.all()
    strings.all()
    empty.all()

    # Demonstrate that all() returns a copy
    all_numbers.append(999)

    # 5. Length operations

    # 6. Generic types demonstration

    # Typed collections
    int_collection: Collection[int] = Collection([10, 20, 30])
    str_collection: Collection[str] = Collection(["hello", "world"])
    list_collection: Collection[list[int]] = Collection([[1, 2], [3, 4]])

    # Add items to typed collections
    int_collection.append(40)
    str_collection.append("python")
    list_collection.append([5, 6])

    # 7. Error handling demonstration

    # Try to get first/last from empty collection
    empty.first()

    with contextlib.suppress(IndexError):
        empty.last()

    # Clear the empty collection and try again
    empty = Collection()
    empty.first()

    # After method with no match

    # 8. String representation


if __name__ == "__main__":
    main()
