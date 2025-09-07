#!/usr/bin/env python3
"""
Example demonstrating Collection first and last methods.
"""

import contextlib

from py_collections import Collection


def main():
    """Demonstrate Collection first and last functionality."""

    # Basic first and last functionality
    numbers = Collection([10, 20, 30, 40, 50])

    # First with predicate functionality

    # First and last after append
    numbers.append(60)

    # First and last with different types
    Collection(["apple", 42, {"key": "value"}])

    # Single element (first and last should be the same)
    Collection([999])

    # Empty collection (will raise error)
    empty = Collection()
    with contextlib.suppress(IndexError):
        empty.first()

    with contextlib.suppress(IndexError):
        empty.last()


if __name__ == "__main__":
    main()
