#!/usr/bin/env python3
"""
Example demonstrating the Collection after method.

This example shows how to use the after method to find the element
that comes after a specific element or predicate match.
"""

from py_collections import Collection


def main():
    # Example 1: Finding element after a specific value
    Collection([1, 2, 3, 4, 5])

    # Example 2: Finding element after predicate match
    Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Example 3: Working with strings
    Collection(["apple", "banana", "cherry", "date", "elderberry"])

    # Example 4: Working with complex objects
    class Person:
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

        def __repr__(self):
            return f"Person({self.name}, {self.age})"

    people = Collection(
        [
            Person("Alice", 25),
            Person("Bob", 30),
            Person("Charlie", 35),
            Person("David", 40),
        ]
    )

    # Find person after someone over 25
    people.after(lambda p: p.age > 25)

    # Find person after someone with name starting with 'B'
    people.after(lambda p: p.name.startswith("B"))

    # Example 5: Edge cases
    Collection()

    Collection([42])

    Collection([1, 2, 2, 3, 2, 4])

    # Example 6: Relationship with first() method
    collection = Collection([1, 2, 3, 4, 5])

    collection.first(lambda x: x % 2 == 0)  # 2
    collection.after(lambda x: x % 2 == 0)  # 3


if __name__ == "__main__":
    main()
