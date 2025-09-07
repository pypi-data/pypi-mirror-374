#!/usr/bin/env python3
"""
Example demonstrating Collection with generic types.
"""

from py_collections import Collection


def main():
    """Demonstrate Collection generic type functionality."""

    # Int collection
    int_collection: Collection[int] = Collection([1, 2, 3])
    int_collection.append(4)

    # String collection
    str_collection: Collection[str] = Collection(["apple", "banana"])
    str_collection.append("cherry")

    # List collection
    list_collection: Collection[list[int]] = Collection([[1, 2], [3, 4]])
    list_collection.append([5, 6])

    # Custom class collection

    class Person:
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

        def __str__(self):
            return f"Person({self.name}, {self.age})"

    person_collection: Collection[Person] = Collection(
        [Person("Alice", 25), Person("Bob", 30)]
    )
    person_collection.append(Person("Charlie", 35))
    person_collection.first()
    person_collection.last()

    # Mixed types (without type annotation)
    Collection([42, "string", [1, 2, 3], {"key": "value"}])


if __name__ == "__main__":
    main()
