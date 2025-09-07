#!/usr/bin/env python3
"""
Example demonstrating Collection initialization methods.
"""

from py_collections import Collection


def main():
    """Demonstrate Collection initialization functionality."""

    # Initialize with an existing array
    my_array = [1, 2, 3]
    Collection(my_array)

    # Initialize empty collection
    empty_collection = Collection()

    empty_collection.append("hello")
    empty_collection.append("world")

    # Collection independence
    collection1 = Collection([1, 2, 3])
    collection2 = Collection([4, 5, 6])

    collection1.append(7)
    collection2.append(8)


if __name__ == "__main__":
    main()
