#!/usr/bin/env python3
"""
Example demonstrating the remove and remove_one methods of the Collection class.

This example shows how to use both methods to remove elements from collections,
either by specific value or by predicate.
"""

from py_collections.collection import Collection


def main():
    print("=== Collection Remove Methods Examples ===\n")

    # Example 1: Basic remove with element
    print("1. Basic remove with element:")
    collection = Collection([1, 2, 2, 3, 4])
    print(f"Original collection: {collection}")
    collection.remove(1)
    print(f"After removing 1: {collection}")
    print()

    # Example 2: Remove all occurrences
    print("2. Remove all occurrences:")
    collection = Collection([1, 2, 2, 3, 2, 4])
    print(f"Original collection: {collection}")
    collection.remove(2)
    print(f"After removing all 2s: {collection}")
    print()

    # Example 3: Remove with predicate
    print("3. Remove with predicate:")
    collection = Collection([1, 2, 2, 3, 4])
    print(f"Original collection: {collection}")
    collection.remove(lambda x: x > 3)
    print(f"After removing elements > 3: {collection}")
    print()

    # Example 4: Remove with complex predicate
    print("4. Remove with complex predicate:")
    collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(f"Original collection: {collection}")
    collection.remove(lambda x: x % 2 == 0)  # Remove even numbers
    print(f"After removing even numbers: {collection}")
    print()

    # Example 5: Remove_one with element
    print("5. Remove_one with element:")
    collection = Collection([1, 2, 2, 3, 4])
    print(f"Original collection: {collection}")
    collection.remove_one(2)
    print(f"After removing first 2: {collection}")
    print()

    # Example 6: Remove_one with predicate
    print("6. Remove_one with predicate:")
    collection = Collection([1, 2, 2, 3, 4])
    print(f"Original collection: {collection}")
    collection.remove_one(lambda x: x == 2)
    print(f"After removing first element == 2: {collection}")
    print()

    # Example 7: Comparison between remove and remove_one
    print("7. Comparison between remove and remove_one:")
    collection1 = Collection([1, 2, 2, 3, 2, 4])
    collection2 = Collection([1, 2, 2, 3, 2, 4])
    print(f"Original collections: {collection1}, {collection2}")

    collection1.remove_one(2)
    print(f"After remove_one(2): {collection1}")

    collection2.remove(2)
    print(f"After remove(2): {collection2}")
    print()

    # Example 8: Remove with strings
    print("8. Remove with strings:")
    collection1 = Collection(["apple", "banana", "apple", "cherry", "apple"])
    collection2 = Collection(["apple", "banana", "apple", "cherry", "apple"])
    print(f"Original collections: {collection1}, {collection2}")

    collection1.remove_one("apple")
    print(f"After remove_one('apple'): {collection1}")

    collection2.remove("apple")
    print(f"After remove('apple'): {collection2}")
    print()

    # Example 9: Remove with mixed types
    print("9. Remove with mixed types:")
    collection = Collection([1, "hello", 2, "world", 3, None, 4])
    print(f"Original collection: {collection}")

    collection.remove("hello")
    print(f"After removing 'hello': {collection}")

    collection.remove(None)
    print(f"After removing None: {collection}")
    print()

    # Example 10: Chaining with other methods
    print("10. Chaining with other methods:")
    collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(f"Original collection: {collection}")

    # Remove even numbers, then get first
    collection.remove(lambda x: x % 2 == 0)
    result = collection.first()
    print(f"First element after removing evens: {result}")

    # Remove numbers > 5, then reverse
    collection.remove(lambda x: x > 5)
    result = collection.reverse()
    print(f"Reversed after removing > 5: {result}")

    # Remove first even number, then filter remaining evens
    collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    collection.remove_one(lambda x: x % 2 == 0)
    result = collection.filter(lambda x: x % 2 == 0)
    print(f"Remaining evens after removing first even: {result}")
    print()

    # Example 11: Remove with complex objects
    print("11. Remove with complex objects:")
    users = Collection(
        [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Alice", "age": 35},
            {"name": "Charlie", "age": 40},
        ]
    )
    print(f"Original users: {users}")

    users.remove_one({"name": "Alice", "age": 30})
    print(f"After removing first Alice (30): {users}")

    users.remove(lambda x: x["name"] == "Alice")
    print(f"After removing all Alices: {users}")
    print()

    # Example 12: Edge cases
    print("12. Edge cases:")

    # Empty collection
    empty = Collection()
    empty.remove(1)
    print(f"Remove from empty: {empty}")

    # Element not found
    collection = Collection([1, 2, 3])
    collection.remove(99)
    print(f"Remove non-existent element: {collection}")

    # Remove all elements
    collection = Collection([1, 1, 1])
    collection.remove(1)
    print(f"Remove all elements: {collection}")
    print()

    # Example 13: Multiple operations
    print("13. Multiple operations:")
    collection = Collection([1, 2, 2, 3, 2, 4, 5, 5])
    print(f"Original collection: {collection}")

    # Remove first 2
    collection.remove_one(2)
    print(f"After first remove_one(2): {collection}")

    # Remove second 2
    collection.remove_one(2)
    print(f"After second remove_one(2): {collection}")

    # Remove all 5s
    collection.remove(5)
    print(f"After remove(5): {collection}")
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
