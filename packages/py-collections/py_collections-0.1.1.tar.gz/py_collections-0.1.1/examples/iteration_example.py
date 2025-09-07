#!/usr/bin/env python3
"""
Example demonstrating iteration functionality of the Collection class.

This example shows how to use Collection objects in for loops and with
various Python built-in functions that work with iterables.
"""

from py_collections import Collection


def main():
    # Basic iteration
    numbers = Collection([1, 2, 3, 4, 5])
    for _item in numbers:
        pass

    # Iteration with different data types
    mixed = Collection(["hello", 42, True, [1, 2, 3], {"key": "value"}])
    for _i, _item in enumerate(mixed):
        pass

    # List comprehension
    numbers = Collection([1, 2, 3, 4, 5])

    # Double each number
    [item * 2 for item in numbers]

    # Filter even numbers
    [item for item in numbers if item % 2 == 0]

    # Built-in functions with iteration
    numbers = Collection([1, 2, 3, 4, 5])

    # Sum
    sum(item for item in numbers)

    # Max and min
    max(item for item in numbers)
    min(item for item in numbers)

    # Any and all
    any(item % 2 == 0 for item in numbers)
    all(item > 0 for item in numbers)

    # Iteration after modifications
    collection = Collection([1, 2, 3])

    collection.append(4)
    collection.append(5)

    for _item in collection:
        pass

    # Empty collection iteration
    empty = Collection()

    count = 0
    for _item in empty:
        count += 1

    # Complex iteration example
    students = Collection(
        [
            {"name": "Alice", "grade": 85},
            {"name": "Bob", "grade": 92},
            {"name": "Charlie", "grade": 78},
            {"name": "Diana", "grade": 95},
        ]
    )

    for _student in students:
        pass

    # Calculate average grade
    total_grade = sum(student["grade"] for student in students)
    total_grade / len(students)

    # Find students with grades above 90
    [student["name"] for student in students if student["grade"] > 90]


if __name__ == "__main__":
    main()
