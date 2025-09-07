#!/usr/bin/env python3
"""
Example demonstrating the before method of the Collection class.

The before method returns the element that comes before the first occurrence
of the target element or predicate match.
"""

from py_collections import Collection


def main():
    # Example 1: Basic before usage with elements
    Collection([1, 2, 3, 4, 5])

    # Example 2: Before with strings
    Collection(["apple", "banana", "cherry", "date", "elderberry"])

    # Example 3: Before with predicates
    Collection([1, 2, 3, 4, 5, 6, 7, 8])

    # Example 4: Before with mixed types
    Collection([1, "hello", 3.14, True, None, "world"])

    # Example 5: Before with duplicates
    Collection([1, 2, 3, 2, 4, 5, 2])

    # Example 6: Edge cases
    Collection()
    Collection([42])
    Collection([1, 2])

    # Example 7: Practical use case - finding context
    log_entries = Collection(
        [
            "INFO: User login",
            "DEBUG: Processing request",
            "ERROR: Database connection failed",
            "INFO: User logout",
            "DEBUG: Cleanup completed",
        ]
    )

    # Find the log entry before the first error
    log_entries.before(lambda entry: "ERROR:" in entry)

    # Find the log entry before the first debug message
    log_entries.before(lambda entry: "DEBUG:" in entry)

    # Example 8: Comparison with after method
    data = Collection([10, 20, 30, 40, 50])

    target = 30
    data.before(target)
    data.after(target)


if __name__ == "__main__":
    main()
