#!/usr/bin/env python3
"""
Example demonstrating the Collection filter method.

This example shows how to use the filter method to create new collections
with elements that satisfy a predicate function.
"""

from py_collections import Collection


def main():
    # Example 1: Basic number filtering
    numbers = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Filter even numbers
    numbers.filter(lambda x: x % 2 == 0)

    # Filter odd numbers
    numbers.filter(lambda x: x % 2 == 1)

    # Filter numbers greater than 5
    numbers.filter(lambda x: x > 5)

    # Example 2: String filtering
    fruits = Collection(["apple", "banana", "cherry", "date", "elderberry", "fig"])

    # Filter fruits starting with 'a'
    fruits.filter(lambda s: s.startswith("a"))

    # Filter fruits with length > 5
    fruits.filter(lambda s: len(s) > 5)

    # Filter fruits containing 'e'
    fruits.filter(lambda s: "e" in s)

    # Example 3: Complex object filtering
    class Person:
        def __init__(self, name: str, age: int, city: str):
            self.name = name
            self.age = age
            self.city = city

        def __repr__(self):
            return f"Person({self.name}, {self.age}, {self.city})"

    people = Collection(
        [
            Person("Alice", 25, "New York"),
            Person("Bob", 30, "Los Angeles"),
            Person("Charlie", 35, "Chicago"),
            Person("David", 40, "Boston"),
            Person("Eve", 22, "Miami"),
            Person("Frank", 28, "Seattle"),
        ]
    )

    # Filter people over 30
    people.filter(lambda p: p.age > 30)

    # Filter people with names starting with 'A'
    people.filter(lambda p: p.name.startswith("A"))

    # Filter people from specific cities
    people.filter(lambda p: p.city in ["New York", "Boston"])

    # Example 4: Mixed type filtering
    mixed = Collection([1, "hello", 3.14, True, [1, 2, 3], None, False, "world"])

    # Filter integers (excluding booleans)
    mixed.filter(lambda x: isinstance(x, int) and not isinstance(x, bool))

    # Filter strings
    mixed.filter(lambda x: isinstance(x, str))

    # Filter booleans
    mixed.filter(lambda x: isinstance(x, bool))

    # Filter truthy values
    mixed.filter(lambda x: bool(x))

    # Example 5: Edge cases

    # Empty collection
    empty_collection = Collection()
    empty_collection.filter(lambda x: x > 0)

    # No matches
    numbers.filter(lambda x: x > 100)

    # All matches
    numbers.filter(lambda x: x > 0)

    # Example 6: Filter chaining
    collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Chain multiple filters
    result = collection.filter(lambda x: x % 2 == 0)  # Even numbers

    result = result.filter(lambda x: x > 5)  # Even numbers > 5

    result = result.filter(lambda x: x < 10)  # Even numbers 5 < x < 10

    # Example 7: Relationship with other methods
    collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Get first even number
    collection.first(lambda x: x % 2 == 0)

    # Get all even numbers
    all_even = collection.filter(lambda x: x % 2 == 0)

    # Verify relationship

    # Get element after first even
    collection.after(lambda x: x % 2 == 0)

    # Get all elements after even numbers
    all_even.filter(lambda x: collection.after(x) is not None)


if __name__ == "__main__":
    main()
