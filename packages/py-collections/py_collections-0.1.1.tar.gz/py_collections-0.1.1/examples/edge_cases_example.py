#!/usr/bin/env python3
"""
Example demonstrating Collection edge cases and error handling.
"""

import contextlib

from py_collections import Collection


def main():
    """Demonstrate Collection edge cases and error handling."""

    # Empty collection operations
    empty = Collection()

    with contextlib.suppress(IndexError):
        empty.first()

    with contextlib.suppress(IndexError):
        empty.last()

    # Single element collection
    Collection([999])

    # Collection with None values
    Collection([None, "hello", None, 42])

    # Collection with empty lists/dicts
    Collection([[], {}, "", 0])

    # Collection independence (deep copy behavior)
    original_list = [1, 2, 3]
    collection1 = Collection(original_list)
    Collection(original_list)

    # Modify original list
    original_list.append(999)

    # Modify collection
    collection1.append(888)


if __name__ == "__main__":
    main()
