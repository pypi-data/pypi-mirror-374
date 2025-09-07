#!/usr/bin/env python3
"""
Example demonstrating the Collection first_or_raise method.

This example shows how to use the first_or_raise method to get the first element
or raise an ItemNotFoundException when no element is found.
"""

import contextlib

from py_collections import Collection, ItemNotFoundException


def main():
    # Example 1: Basic usage when element exists
    collection = Collection([1, 2, 3, 4, 5])

    # Get first element
    collection.first_or_raise()

    # Get first even number
    collection.first_or_raise(lambda x: x % 2 == 0)

    # Get first number > 3
    collection.first_or_raise(lambda x: x > 3)

    # Example 2: String collection
    fruits = Collection(["apple", "banana", "cherry", "date"])

    # Get first fruit starting with 'b'
    fruits.first_or_raise(lambda s: s.startswith("b"))

    # Get first fruit with length > 5
    fruits.first_or_raise(lambda s: len(s) > 5)

    # Example 3: Complex objects
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

    # Find first person over 25
    people.first_or_raise(lambda p: p.age > 25)

    # Find first person with name starting with 'C'
    people.first_or_raise(lambda p: p.name.startswith("C"))

    # Example 4: Exception handling

    # Empty collection
    empty_collection = Collection()

    with contextlib.suppress(ItemNotFoundException):
        empty_collection.first_or_raise()

    # No matching element
    collection = Collection([1, 2, 3, 4, 5])

    with contextlib.suppress(ItemNotFoundException):
        collection.first_or_raise(lambda x: x > 100)

    with contextlib.suppress(ItemNotFoundException):
        collection.first_or_raise(lambda x: x < 0)

    # Example 5: Comparison with first() method
    collection = Collection([1, 2, 3, 4, 5])

    # When element exists, both methods return the same result
    collection.first(lambda x: x % 2 == 0)
    collection.first_or_raise(lambda x: x % 2 == 0)

    # When element doesn't exist, first() returns None, first_or_raise() raises exception

    with contextlib.suppress(ItemNotFoundException):
        collection.first_or_raise(lambda x: x > 100)

    # Example 6: Practical use case

    # Simulate finding a user by ID
    class User:
        def __init__(self, id: int, name: str):
            self.id = id
            self.name = name

        def __repr__(self):
            return f"User({self.id}, {self.name})"

    users = Collection([User(1, "Alice"), User(2, "Bob"), User(3, "Charlie")])

    # Find user with ID 2
    with contextlib.suppress(ItemNotFoundException):
        user = users.first_or_raise(lambda u: u.id == 2)

    # Try to find non-existent user
    with contextlib.suppress(ItemNotFoundException):
        user = users.first_or_raise(lambda u: u.id == 999)

    # Example 7: Error handling patterns

    def find_user_by_id(users_collection, user_id):
        """Helper function to find user by ID with proper error handling."""
        try:
            return users_collection.first_or_raise(lambda u: u.id == user_id)
        except ItemNotFoundException:
            return None

    # Test the helper function
    user = find_user_by_id(users, 1)
    if user:
        pass

    user = find_user_by_id(users, 999)
    if user:
        pass


if __name__ == "__main__":
    main()
