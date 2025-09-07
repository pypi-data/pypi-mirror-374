#!/usr/bin/env python3
"""
Example demonstrating the clone method of the Collection class.

This example shows how to use the clone method to create a new collection
with the same items as the original.
"""

from py_collections.collection import Collection


def main():
    print("=== Collection Clone Method Examples ===\n")

    # Example 1: Basic cloning
    print("1. Basic cloning:")
    original = Collection([1, 2, 3, 4, 5])
    cloned = original.clone()
    print(f"Original: {original}")
    print(f"Cloned: {cloned}")
    print(f"Same object? {original is cloned}")
    print(f"Same content? {original.all() == cloned.all()}")
    print()

    # Example 2: Cloning with different types
    print("2. Cloning with different types:")
    original = Collection([1, "hello", True, None, 3.14])
    cloned = original.clone()
    print(f"Original: {original}")
    print(f"Cloned: {cloned}")
    print()

    # Example 3: Cloning empty collection
    print("3. Cloning empty collection:")
    original = Collection()
    cloned = original.clone()
    print(f"Original: {original}")
    print(f"Cloned: {cloned}")
    print(f"Same object? {original is cloned}")
    print()

    # Example 4: Independence of cloned collection
    print("4. Independence of cloned collection:")
    original = Collection([1, 2, 3])
    cloned = original.clone()
    print(f"Original: {original}")
    print(f"Cloned: {cloned}")

    # Modify the original
    original.append(4)
    print(f"After modifying original: {original}")
    print(f"Cloned unchanged: {cloned}")

    # Modify the clone
    cloned.append(5)
    print(f"Original unchanged: {original}")
    print(f"After modifying clone: {cloned}")
    print()

    # Example 5: Cloning with complex objects
    print("5. Cloning with complex objects:")
    original = Collection([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])
    cloned = original.clone()
    print(f"Original: {original}")
    print(f"Cloned: {cloned}")
    print()

    # Example 6: Cloning with duplicates
    print("6. Cloning with duplicate elements:")
    original = Collection([1, 2, 2, 3, 2, 4])
    cloned = original.clone()
    print(f"Original: {original}")
    print(f"Cloned: {cloned}")
    print()

    # Example 7: Chaining clone with other methods
    print("7. Chaining clone with other methods:")
    original = Collection([1, 2, 3, 4, 5])

    # Clone and then reverse
    reversed_clone = original.clone().reverse()
    print(f"Original: {original}")
    print(f"Reversed clone: {reversed_clone}")

    # Clone and then filter
    filtered_clone = original.clone().filter(lambda x: x % 2 == 0)
    print(f"Filtered clone (even numbers): {filtered_clone}")
    print()

    # Example 8: Multiple clones
    print("8. Multiple clones:")
    original = Collection([1, 2, 3])

    clone1 = original.clone()
    clone2 = original.clone()
    clone3 = original.clone()

    print(f"Original: {original}")
    print(f"Clone 1: {clone1}")
    print(f"Clone 2: {clone2}")
    print(f"Clone 3: {clone3}")

    # All are different objects
    print(
        f"All different objects? {original is not clone1 and clone1 is not clone2 and clone2 is not clone3}"
    )
    print()

    # Example 9: Cloning after modifications
    print("9. Cloning after modifications:")
    original = Collection([1, 2, 3])
    original.append(4)
    original.remove(2)

    cloned = original.clone()
    print(f"Modified original: {original}")
    print(f"Cloned: {cloned}")
    print()

    # Example 10: Cloning with mutable objects
    print("10. Cloning with mutable objects:")
    original = Collection([[1, 2], [3, 4], [5, 6]])
    cloned = original.clone()
    print(f"Original: {original}")
    print(f"Cloned: {cloned}")

    # Modify a mutable object in the original
    original.all()[0].append(7)
    print(f"After modifying original's first list: {original}")
    print(f"Cloned affected: {cloned}")
    print("Note: This is expected behavior since we copy references to mutable objects")
    print()

    # Example 11: Performance demonstration
    print("11. Performance demonstration:")
    large_original = Collection(list(range(1000)))
    print(f"Large collection (first 5 items): {large_original.all()[:5]}...")

    large_cloned = large_original.clone()
    print(f"Large cloned (first 5 items): {large_cloned.all()[:5]}...")
    print(f"Same content? {large_original.all() == large_cloned.all()}")
    print(f"Different objects? {large_original is not large_cloned}")
    print()

    # Example 12: Clone vs copy comparison
    print("12. Clone vs copy comparison:")
    original = Collection([1, 2, 3])

    # Using clone method
    cloned = original.clone()

    # Using copy constructor
    copied = Collection(original.all())

    print(f"Original: {original}")
    print(f"Cloned: {cloned}")
    print(f"Copied: {copied}")
    print(f"Clone same as original? {original is cloned}")
    print(f"Copy same as original? {original is copied}")
    print(f"Clone same as copy? {cloned is copied}")
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
