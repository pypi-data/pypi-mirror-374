#!/usr/bin/env python3
"""
Example demonstrating Collection first method with predicate functions.
"""

import contextlib

from py_collections import Collection


def main():
    """Demonstrate Collection first method with predicate functionality."""

    # Basic first without predicate (original behavior)
    numbers = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # First with predicate - find first even number
    numbers.first(lambda x: x % 2 == 0)

    # First with predicate - find first number greater than 5
    numbers.first(lambda x: x > 5)

    # First with predicate - find first number divisible by 3
    numbers.first(lambda x: x % 3 == 0)

    # String collection examples
    words = Collection(["apple", "banana", "cherry", "date", "elderberry"])

    # Find first word starting with 'b'
    words.first(lambda word: word.startswith("b"))

    # Find first word with length > 5
    words.first(lambda word: len(word) > 5)

    # Find first word containing 'e'
    words.first(lambda word: "e" in word)

    # Mixed type collection examples
    mixed = Collection([1, "hello", 3.14, True, [1, 2, 3], {"key": "value"}])

    # Find first string
    mixed.first(lambda x: isinstance(x, str))

    # Find first number (int or float)
    mixed.first(lambda x: isinstance(x, int | float))

    # Find first list
    mixed.first(lambda x: isinstance(x, list))

    # Custom class examples

    class Person:
        def __init__(self, name: str, age: int, city: str):
            self.name = name
            self.age = age
            self.city = city

        def __str__(self):
            return f"Person({self.name}, {self.age}, {self.city})"

    people = Collection(
        [
            Person("Alice", 25, "New York"),
            Person("Bob", 30, "San Francisco"),
            Person("Charlie", 35, "Chicago"),
            Person("Diana", 28, "Boston"),
            Person("Eve", 22, "Los Angeles"),
        ]
    )

    # Find first person over 25
    people.first(lambda person: person.age > 25)

    # Find first person from New York
    people.first(lambda person: person.city == "New York")

    # Find first person with name starting with 'C'
    people.first(lambda person: person.name.startswith("C"))

    # Error handling examples

    # Try to find first number > 100 (no such number exists)
    with contextlib.suppress(IndexError):
        numbers.first(lambda x: x > 100)

    # Try to find first word starting with 'z' (no such word exists)
    with contextlib.suppress(IndexError):
        words.first(lambda word: word.startswith("z"))

    # Empty collection
    empty = Collection()
    with contextlib.suppress(IndexError):
        empty.first(lambda x: x > 0)


if __name__ == "__main__":
    main()
