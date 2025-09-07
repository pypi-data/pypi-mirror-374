#!/usr/bin/env python3
"""
Example demonstrating the exists() method of the Collection class.

This example shows how to use the exists() method to check if elements
exist in a collection based on various conditions.
"""

from py_collections import Collection


def main():
    # Example 1: Basic existence check
    Collection()
    Collection([1, 2, 3, 4, 5])

    # Example 2: Checking for specific values
    Collection(["apple", "banana", "cherry", "date"])

    # Example 3: Numeric conditions
    Collection([85, 92, 78, 96, 88, 91])

    # Example 4: Complex objects

    class Person:
        def __init__(self, name, age, city):
            self.name = name
            self.age = age
            self.city = city

        def __str__(self):
            return f"{self.name} ({self.age}, {self.city})"

    Collection(
        [
            Person("Alice", 25, "New York"),
            Person("Bob", 30, "Los Angeles"),
            Person("Charlie", 35, "Chicago"),
            Person("Diana", 28, "Boston"),
        ]
    )

    # Example 5: Multiple conditions
    Collection(
        [
            {"name": "Laptop", "price": 999, "in_stock": True},
            {"name": "Mouse", "price": 25, "in_stock": False},
            {"name": "Keyboard", "price": 150, "in_stock": True},
            {"name": "Monitor", "price": 300, "in_stock": True},
        ]
    )

    # Example 6: Edge cases
    Collection([1, None, "hello", 0, False, ""])

    # Example 7: Performance demonstration
    Collection(list(range(10000)))

    # Check for first element (should be fast)


if __name__ == "__main__":
    main()
