#!/usr/bin/env python3
"""
Example demonstrating the chunk method of the Collection class.

The chunk method splits a collection into smaller collections of the specified size.
"""

from py_collections import Collection


def main():
    # Example 1: Basic chunking
    numbers = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9])
    chunks = numbers.chunk(3)
    for _i, _chunk in enumerate(chunks):
        pass

    # Example 2: Chunking with size larger than collection
    small_collection = Collection([1, 2, 3])
    large_chunks = small_collection.chunk(5)
    for _i, _chunk in enumerate(large_chunks):
        pass

    # Example 3: Chunking with size 1
    words = Collection(["apple", "banana", "cherry", "date"])
    single_chunks = words.chunk(1)
    for _i, _chunk in enumerate(single_chunks):
        pass

    # Example 4: Chunking with mixed types
    mixed = Collection([1, "hello", 3.14, True, None, "world"])
    mixed_chunks = mixed.chunk(2)
    for _i, _chunk in enumerate(mixed_chunks):
        pass

    # Example 5: Empty collection
    empty = Collection()
    empty.chunk(3)

    # Example 6: Error handling
    try:
        numbers.chunk(0)  # This should raise ValueError
    except ValueError:
        pass

    try:
        numbers.chunk(-1)  # This should raise ValueError
    except ValueError:
        pass

    try:
        numbers.chunk(2.5)  # This should raise ValueError
    except ValueError:
        pass

    # Example 7: Practical use case - processing data in batches
    data = Collection([f"item_{i}" for i in range(1, 11)])
    batch_size = 3
    batches = data.chunk(batch_size)

    for _batch_num, batch in enumerate(batches, 1):
        # Simulate processing each batch
        for _item in batch.all():
            pass


if __name__ == "__main__":
    main()
