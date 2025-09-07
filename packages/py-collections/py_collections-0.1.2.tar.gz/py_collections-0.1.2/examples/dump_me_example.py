#!/usr/bin/env python3
"""
Example demonstrating the dump_me() and dump_me_and_die() methods of the Collection class.

This example shows how to use both debugging methods to inspect collection contents.
"""

from py_collections import Collection


def main():
    # Example 1: Basic dump_me() usage
    numbers = Collection([1, 2, 3, 4, 5])

    numbers.dump_me()

    # Example 2: dump_me() with different data types
    mixed = Collection([42, "hello", 3.14, True, None, [1, 2, 3], {"key": "value"}])
    mixed.dump_me()

    # Example 3: dump_me() with empty collection
    empty = Collection()
    empty.dump_me()

    # Example 4: dump_me() with custom objects

    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age

        def __str__(self):
            return f"{self.name}({self.age})"

    people = Collection([Person("Alice", 25), Person("Bob", 30), Person("Charlie", 35)])

    people.dump_me()

    # Example 5: dump_me_and_die() usage
    Collection(["apple", "banana", "cherry"])

    # Uncomment the next line to see dump_me_and_die() in action
    # test_collection.dump_me_and_die()

    # Example 6: Practical debugging scenario
    data = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Simulate some processing
    filtered = data.filter(lambda x: x % 2 == 0)
    filtered.dump_me()

    # Continue processing
    doubled = Collection([x * 2 for x in filtered.all()])
    doubled.dump_me()

    # Example 7: Comparison between methods
    sample = Collection(["a", "b", "c"])

    sample.dump_me()

    # sample.dump_me_and_die()
    # print("This line would not execute if dump_me_and_die() was called")


if __name__ == "__main__":
    main()
