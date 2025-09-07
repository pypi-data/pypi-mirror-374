#!/usr/bin/env python3
"""
Example demonstrating Collection all method.
"""

from py_collections import Collection


def main():
    """Demonstrate Collection all functionality."""

    # Basic all functionality
    collection = Collection([1, 2, 3, 4, 5])
    collection.all()

    # Get all items (returns a copy)
    items = collection.all()
    items.append(999)  # This won't affect the original collection

    # All items with different types
    mixed_collection = Collection([42, "string", [1, 2, 3], {"key": "value"}])
    mixed_collection.all()

    # Empty collection
    empty_collection = Collection()
    empty_collection.all()


if __name__ == "__main__":
    main()
