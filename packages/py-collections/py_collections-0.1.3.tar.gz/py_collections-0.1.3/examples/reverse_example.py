#!/usr/bin/env python3
"""
Example demonstrating the reverse method of the Collection class.

This example shows how to use the reverse method to create a new collection
with items in reverse order.
"""

from py_collections.collection import Collection


def main():
    print("=== Collection Reverse Method Examples ===\n")

    # Example 1: Basic reverse with numbers
    print("1. Basic reverse with numbers:")
    collection = Collection([1, 2, 3, 4, 5])
    print(f"Original collection: {collection}")
    reversed_collection = collection.reverse()
    print(f"Reversed collection: {reversed_collection}")
    print(f"Original unchanged: {collection}")
    print()

    # Example 2: Reverse with strings
    print("2. Reverse with strings:")
    collection = Collection(["apple", "banana", "cherry", "date"])
    print(f"Original collection: {collection}")
    reversed_collection = collection.reverse()
    print(f"Reversed collection: {reversed_collection}")
    print()

    # Example 3: Reverse empty collection
    print("3. Reverse empty collection:")
    empty_collection = Collection()
    print(f"Empty collection: {empty_collection}")
    reversed_empty = empty_collection.reverse()
    print(f"Reversed empty: {reversed_empty}")
    print()

    # Example 4: Reverse with mixed types
    print("4. Reverse with mixed types:")
    collection = Collection([1, "hello", True, None, 3.14])
    print(f"Original collection: {collection}")
    reversed_collection = collection.reverse()
    print(f"Reversed collection: {reversed_collection}")
    print()

    # Example 5: Multiple reverses
    print("5. Multiple reverses:")
    collection = Collection([1, 2, 3, 4])
    print(f"Original: {collection}")

    reversed1 = collection.reverse()
    print(f"First reverse: {reversed1}")

    reversed2 = reversed1.reverse()
    print(f"Second reverse: {reversed2}")

    reversed3 = reversed2.reverse()
    print(f"Third reverse: {reversed3}")
    print()

    # Example 6: Reverse with complex objects
    print("6. Reverse with complex objects:")
    users = Collection(
        [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]
    )
    print(f"Original users: {users}")
    reversed_users = users.reverse()
    print(f"Reversed users: {reversed_users}")
    print()

    # Example 7: Chaining reverse with other methods
    print("7. Chaining reverse with other methods:")
    numbers = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(f"Original numbers: {numbers}")

    # Reverse and then filter even numbers
    reversed_even = numbers.reverse().filter(lambda x: x % 2 == 0)
    print(f"Reversed even numbers: {reversed_even}")

    # Reverse and get first element
    first_after_reverse = numbers.reverse().first()
    print(f"First element after reverse: {first_after_reverse}")

    # Reverse and get last element
    last_after_reverse = numbers.reverse().last()
    print(f"Last element after reverse: {last_after_reverse}")
    print()

    # Example 8: Reverse with duplicates
    print("8. Reverse with duplicate elements:")
    collection = Collection([1, 2, 2, 3, 2, 4, 5, 5])
    print(f"Original with duplicates: {collection}")
    reversed_collection = collection.reverse()
    print(f"Reversed with duplicates: {reversed_collection}")
    print()

    # Example 9: Demonstrating immutability
    print("9. Demonstrating immutability:")
    original_items = [10, 20, 30, 40, 50]
    collection = Collection(original_items)
    print(f"Original collection: {collection}")

    reversed_collection = collection.reverse()
    print(f"Reversed collection: {reversed_collection}")

    # Modify the original list
    original_items.append(60)
    print(f"After modifying original list: {collection}")
    print(f"Reversed collection unchanged: {reversed_collection}")
    print()

    # Example 10: Performance demonstration
    print("10. Performance demonstration:")
    large_collection = Collection(list(range(1000)))
    print(f"Large collection (first 5 items): {large_collection.all()[:5]}...")

    reversed_large = large_collection.reverse()
    print(f"Reversed large collection (first 5 items): {reversed_large.all()[:5]}...")
    print(f"Last 5 items of reversed: {reversed_large.all()[-5:]}")
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
