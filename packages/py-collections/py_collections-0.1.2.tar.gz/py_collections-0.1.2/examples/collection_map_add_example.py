#!/usr/bin/env python3
"""
Example demonstrating the new CollectionMap add method and modified get method.

This example shows how to use the add method to build collections incrementally
and how the get method now returns empty collections by default.
"""

from py_collections import Collection, CollectionMap


def main():
    # Example 1: Building collections incrementally with add

    cmap = CollectionMap()

    # Add items to new keys
    cmap.add("fruits", ["apple", "banana"])
    cmap.add("vegetables", ["carrot", "broccoli"])
    cmap.add("numbers", [1, 2, 3])

    # Add more items to existing keys
    cmap.add("fruits", ["cherry", "date"])
    cmap.add("vegetables", "spinach")  # Single item
    cmap.add("numbers", Collection([4, 5]))  # Collection object

    # Add to a completely new key
    cmap.add("colors", ["red", "blue", "green"])

    # Example 2: Using get with empty collection default

    # Get existing key
    cmap.get("fruits")

    # Get non-existing key - returns empty collection
    cmap.get("missing_key")

    # Get with custom default
    cmap.get("another_missing", Collection(["default", "value"]))

    # Example 3: Building collections from different sources

    users_cmap = CollectionMap()

    # Add users from different sources
    users_cmap.add(
        "admin",
        [
            {"name": "Alice", "role": "admin", "id": 1},
            {"name": "Bob", "role": "admin", "id": 2},
        ],
    )

    # Add from existing Collection
    regular_users = Collection(
        [
            {"name": "Charlie", "role": "user", "id": 3},
            {"name": "Diana", "role": "user", "id": 4},
        ]
    )
    users_cmap.add("user", regular_users)

    # Add single user
    users_cmap.add("guest", {"name": "Eve", "role": "guest", "id": 5})

    # Get and work with collections
    users_cmap.get("admin")
    users_cmap.get("user")
    users_cmap.get("guest")

    # Example 4: Incremental data collection

    orders_cmap = CollectionMap()

    # Simulate collecting orders over time

    # First batch
    orders_cmap.add(
        "pending",
        [
            {"id": 1, "customer": "Alice", "amount": 100},
            {"id": 2, "customer": "Bob", "amount": 150},
        ],
    )

    # Second batch
    orders_cmap.add(
        "pending",
        [
            {"id": 3, "customer": "Charlie", "amount": 200},
            {"id": 4, "customer": "Diana", "amount": 75},
        ],
    )

    # Single order
    orders_cmap.add("pending", {"id": 5, "customer": "Eve", "amount": 300})

    # Move some to completed
    pending_orders = orders_cmap.get("pending")
    orders_cmap.get("completed")  # Empty collection

    # Move first two orders to completed
    orders_to_complete = pending_orders.all()[:2]
    orders_cmap.add("completed", orders_to_complete)

    # Remove completed orders from pending
    remaining_pending = pending_orders.all()[2:]
    orders_cmap["pending"] = Collection(remaining_pending)

    # Example 5: Working with empty collections safely

    # Create empty CollectionMap
    empty_cmap = CollectionMap()

    # Get non-existing keys - all return empty collections
    empty_fruits = empty_cmap.get("fruits")
    empty_numbers = empty_cmap.get("numbers")
    empty_users = empty_cmap.get("users")

    # All are empty collections, not None
    assert len(empty_fruits) == 0
    assert len(empty_numbers) == 0
    assert len(empty_users) == 0

    # Can safely iterate over empty collections
    for _fruit in empty_fruits:
        pass  # This won't execute

    # Can safely use Collection methods
    empty_fruits.first()

    # Add to empty collections
    empty_cmap.add("fruits", ["apple", "banana"])
    empty_cmap.add("numbers", [1, 2, 3])

    # Example 6: Complex workflow

    # Simulate a data processing pipeline
    data_cmap = CollectionMap()

    # Phase 1: Collect raw data
    data_cmap.add("raw", [1, 2, 3, 4, 5])
    data_cmap.add("raw", [6, 7, 8, 9, 10])

    # Phase 2: Process data
    raw_data = data_cmap.get("raw")
    processed_data = []

    for item in raw_data:
        if item % 2 == 0:
            processed_data.append({"value": item, "type": "even"})
        else:
            processed_data.append({"value": item, "type": "odd"})

    data_cmap.add("processed", processed_data)

    # Phase 3: Filter by type
    processed_data = data_cmap.get("processed")
    even_data = [item for item in processed_data if item["type"] == "even"]
    odd_data = [item for item in processed_data if item["type"] == "odd"]

    data_cmap.add("even", even_data)
    data_cmap.add("odd", odd_data)

    # Show final state


if __name__ == "__main__":
    main()
