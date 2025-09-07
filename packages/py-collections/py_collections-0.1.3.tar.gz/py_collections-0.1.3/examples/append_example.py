#!/usr/bin/env python3
"""
Example demonstrating Collection append method.
"""

from py_collections import Collection


def main():
    """Demonstrate Collection append functionality."""

    # Basic append functionality
    collection = Collection([1, 2, 3])

    collection.append(4)
    collection.append(5)

    # Append different data types
    mixed_collection = Collection()
    mixed_collection.append(42)
    mixed_collection.append("string")
    mixed_collection.append([1, 2, 3])
    mixed_collection.append({"key": "value"})

    # Append to empty collection
    empty_collection = Collection()

    empty_collection.append("hello")
    empty_collection.append("world")


if __name__ == "__main__":
    main()
