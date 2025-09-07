#!/usr/bin/env python3
"""
Example demonstrating the extend method of the Collection class.

This example shows how to use the extend method to add multiple items
from a list or another collection to an existing collection.
"""

from py_collections.collection import Collection


def main():
    print("=== Collection Extend Method Examples ===\n")

    # Example 1: Extending with a list
    print("1. Extending with a list:")
    collection = Collection([1, 2, 3])
    print(f"Original collection: {collection}")
    collection.extend([4, 5, 6])
    print(f"After extending with [4, 5, 6]: {collection}")
    print(f"All items: {collection.all()}")
    print()

    # Example 2: Extending with another collection
    print("2. Extending with another collection:")
    collection = Collection(["a", "b", "c"])
    other_collection = Collection(["d", "e", "f"])
    print(f"Original collection: {collection}")
    print(f"Other collection: {other_collection}")
    collection.extend(other_collection)
    print(f"After extending with other collection: {collection}")
    print(f"All items: {collection.all()}")
    print()

    # Example 3: Extending multiple times
    print("3. Extending multiple times:")
    collection = Collection([1])
    print(f"Starting with: {collection}")

    collection.extend([2, 3])
    print(f"After first extend: {collection}")

    collection.extend(Collection([4, 5]))
    print(f"After second extend: {collection}")

    collection.extend([6, 7, 8])
    print(f"After third extend: {collection}")
    print(f"Final result: {collection.all()}")
    print()

    # Example 4: Extending empty collections
    print("4. Extending empty collections:")
    empty_collection = Collection()
    print(f"Empty collection: {empty_collection}")
    empty_collection.extend([1, 2, 3])
    print(f"After extending: {empty_collection}")
    print()

    # Example 5: Extending with empty list/collection
    print("5. Extending with empty list/collection:")
    collection = Collection([1, 2, 3])
    print(f"Original collection: {collection}")
    collection.extend([])
    print(f"After extending with empty list: {collection}")
    collection.extend(Collection())
    print(f"After extending with empty collection: {collection}")
    print()

    # Example 6: Mixed types
    print("6. Extending with mixed types:")
    collection = Collection(["hello", "world"])
    collection.extend([1, 2, 3, None, True])
    print(f"Collection with mixed types: {collection}")
    print(f"All items: {collection.all()}")
    print()

    # Example 7: Demonstrating that original collection is preserved
    print("7. Original collection preservation:")
    original = Collection([10, 20, 30])
    to_extend = Collection([40, 50, 60])
    print(f"Original collection: {original}")
    print(f"Collection to extend with: {to_extend}")

    original.extend(to_extend)
    print(f"After extending: {original}")
    print(f"Extended collection still intact: {to_extend}")
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
