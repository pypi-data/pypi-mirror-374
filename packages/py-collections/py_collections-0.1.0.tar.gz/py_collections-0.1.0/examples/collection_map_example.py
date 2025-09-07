#!/usr/bin/env python3
"""
Example demonstrating the CollectionMap functionality.

This example shows how to use CollectionMap to work with grouped data
in a more structured way than regular dictionaries.
"""

from py_collections import Collection, CollectionMap


def main():
    # Example 1: Basic CollectionMap usage

    # Create from group_by result
    users = Collection(
        [
            {"name": "Alice", "department": "Engineering", "age": 25},
            {"name": "Bob", "department": "Sales", "age": 30},
            {"name": "Charlie", "department": "Engineering", "age": 35},
            {"name": "Diana", "department": "Marketing", "age": 28},
            {"name": "Eve", "department": "Engineering", "age": 32},
        ]
    )

    # Convert group_by result to CollectionMap
    grouped_dict = users.group_by("department")
    cmap = CollectionMap(grouped_dict)

    # Example 2: Working with groups

    # Access individual groups
    engineering = cmap["Engineering"]

    # Use Collection methods on groups
    [user["name"] for user in engineering.all()]

    # Find youngest engineer
    engineering.first(
        lambda user: user["age"] == min(user["age"] for user in engineering.all())
    )

    # Example 3: CollectionMap operations

    # Get group sizes
    cmap.group_sizes()

    # Find largest and smallest groups
    largest_key, largest_group = cmap.largest_group()
    smallest_key, smallest_group = cmap.smallest_group()

    # Filter groups by size
    cmap.filter_by_size(min_size=2)

    # Example 4: Flattening and mapping

    # Flatten all groups into one collection
    cmap.flatten()

    # Map over all groups
    group_stats = cmap.map(
        lambda collection: {
            "count": len(collection),
            "avg_age": sum(user["age"] for user in collection.all()) / len(collection),
            "names": [user["name"] for user in collection.all()],
        }
    )

    for _dept, _stats in group_stats.items():
        pass

    # Example 5: Creating CollectionMap from scratch

    # Empty CollectionMap
    new_cmap = CollectionMap()

    # Add groups
    new_cmap["fruits"] = ["apple", "banana", "cherry"]
    new_cmap["vegetables"] = ["carrot", "broccoli"]
    new_cmap["numbers"] = [1, 2, 3, 4, 5]

    # Use setdefault to add to existing group
    new_cmap.setdefault("fruits").append("date")

    # Create new group with setdefault
    new_cmap.setdefault("colors", ["red", "blue"])

    # Example 6: Advanced filtering and operations

    # Create a more complex CollectionMap
    orders = Collection(
        [
            {"id": 1, "customer": "Alice", "amount": 100, "status": "completed"},
            {"id": 2, "customer": "Bob", "amount": 150, "status": "pending"},
            {"id": 3, "customer": "Alice", "amount": 200, "status": "completed"},
            {"id": 4, "customer": "Charlie", "amount": 75, "status": "cancelled"},
            {"id": 5, "customer": "Bob", "amount": 300, "status": "completed"},
        ]
    )

    orders_by_customer = CollectionMap(orders.group_by("customer"))

    # Filter customers with multiple orders
    orders_by_customer.filter_by_size(min_size=2)

    # Calculate customer statistics
    customer_stats = orders_by_customer.map(
        lambda customer_orders: {
            "total_orders": len(customer_orders),
            "total_amount": sum(order["amount"] for order in customer_orders.all()),
            "completed_orders": len(
                customer_orders.filter(lambda order: order["status"] == "completed")
            ),
            "pending_orders": len(
                customer_orders.filter(lambda order: order["status"] == "pending")
            ),
        }
    )

    for _customer, _stats in customer_stats.items():
        pass

    # Example 7: Working with different data types

    mixed_cmap = CollectionMap()

    # Add different types of data
    mixed_cmap["integers"] = [1, 2, 3, 4, 5]
    mixed_cmap["strings"] = ["hello", "world", "python"]
    mixed_cmap["mixed"] = [1, "hello", True, 3.14]

    # Apply different operations to each group
    results = mixed_cmap.map(
        lambda collection: {
            "type": type(collection.first()).__name__
            if collection.first()
            else "empty",
            "count": len(collection),
            "sum": sum(
                item for item in collection.all() if isinstance(item, int | float)
            ),
            "strings": [str(item) for item in collection.all()],
        }
    )

    for _group, _analysis in results.items():
        pass

    # Example 8: Integration with group_by

    # Create a CollectionMap directly from group_by
    students = Collection(
        [
            {"name": "Alice", "grade": "A", "subject": "Math"},
            {"name": "Bob", "grade": "B", "subject": "Math"},
            {"name": "Charlie", "grade": "A", "subject": "Science"},
            {"name": "Diana", "grade": "B", "subject": "Science"},
            {"name": "Eve", "grade": "A", "subject": "Math"},
        ]
    )

    # Group by multiple criteria and convert to CollectionMap
    by_grade_subject = CollectionMap(
        students.group_by(lambda student: (student["grade"], student["subject"]))
    )

    # Analyze each group
    for (_grade, _subject), student_group in by_grade_subject.items():
        [student["name"] for student in student_group.all()]


if __name__ == "__main__":
    main()
