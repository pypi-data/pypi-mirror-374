#!/usr/bin/env python3
"""
Example demonstrating the take method of the Collection class.

The take method returns a new collection with the specified number of items.
- Positive count: takes from the beginning
- Negative count: takes from the end
"""

from py_collections import Collection


def main():
    print("=== Collection.take() Method Examples ===\n")

    # Create a sample collection
    numbers = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(f"Original collection: {numbers}")
    print(f"Length: {len(numbers)}\n")

    # Example 1: Take positive number of items from the beginning
    print("1. Taking positive number of items (from beginning):")
    print(f"   numbers.take(3).all() => {numbers.take(3).all()}")
    print(f"   numbers.take(5).all() => {numbers.take(5).all()}")
    print(f"   numbers.take(1).all() => {numbers.take(1).all()}")
    print()

    # Example 2: Take negative number of items from the end
    print("2. Taking negative number of items (from end):")
    print(f"   numbers.take(-3).all() => {numbers.take(-3).all()}")
    print(f"   numbers.take(-5).all() => {numbers.take(-5).all()}")
    print(f"   numbers.take(-1).all() => {numbers.take(-1).all()}")
    print()

    # Example 3: Edge cases
    print("3. Edge cases:")
    print(f"   numbers.take(0).all() => {numbers.take(0).all()}")
    print(
        f"   numbers.take(15).all() => {numbers.take(15).all()} (more than available)"
    )
    print(
        f"   numbers.take(-15).all() => {numbers.take(-15).all()} (negative more than available)"
    )
    print()

    # Example 4: Working with different data types
    print("4. Working with different data types:")
    mixed = Collection(["apple", "banana", "cherry", "date", "elderberry"])
    print(f"   Mixed collection: {mixed}")
    print(f"   mixed.take(2).all() => {mixed.take(2).all()}")
    print(f"   mixed.take(-2).all() => {mixed.take(-2).all()}")
    print()

    # Example 5: Original collection remains unchanged
    print("5. Original collection remains unchanged:")
    original = Collection([1, 2, 3, 4, 5])
    print(f"   Original: {original}")
    result = original.take(2)
    print(f"   After take(2): {result}")
    print(f"   Original still: {original}")
    print(f"   Original unchanged: {original.all() == [1, 2, 3, 4, 5]}")
    print()

    # Example 6: Empty collection
    print("6. Empty collection:")
    empty = Collection()
    print(f"   Empty collection: {empty}")
    print(f"   empty.take(3).all() => {empty.take(3).all()}")
    print(f"   empty.take(-3).all() => {empty.take(-3).all()}")
    print()

    # Example 7: Practical use cases
    print("7. Practical use cases:")

    # Pagination example
    users = Collection(["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"])
    page_size = 3
    page_1 = users.take(page_size)
    page_2 = users.take(-(len(users) - page_size))

    print(f"   Users: {users}")
    print(f"   Page 1 (first 3): {page_1.all()}")
    print(f"   Page 2 (remaining): {page_2.all()}")
    print()

    # Recent items example
    transactions = Collection([100, 200, 150, 300, 250, 180, 220])
    recent_3 = transactions.take(-3)
    print(f"   All transactions: {transactions}")
    print(f"   Recent 3 transactions: {recent_3.all()}")
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
