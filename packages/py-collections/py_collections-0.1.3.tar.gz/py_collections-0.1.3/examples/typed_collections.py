#!/usr/bin/env python3
"""
Example demonstrating typed collections with proper type annotations.
This file shows how to use the Collection class with specific types.
"""

from py_collections import Collection, T


def demonstrate_int_collection():
    """Demonstrate Collection[int] usage."""

    # Type-annotated int collection
    numbers: Collection[int] = Collection([1, 2, 3, 4, 5])

    # Append more integers
    numbers.append(6)
    numbers.append(7)

    # Get the first and last numbers (type checker knows they're ints)
    numbers.first()
    numbers.last()

    # Get all numbers using all() method
    all_numbers = numbers.all()

    # Sum all numbers
    sum(all_numbers)


def demonstrate_str_collection():
    """Demonstrate Collection[str] usage."""

    # Type-annotated string collection
    words: Collection[str] = Collection(["hello", "world", "python"])

    # Append more strings
    words.append("collection")
    words.append("types")

    # Get the first and last words (type checker knows they're strs)
    words.first()
    words.last()

    # Get all words using all() method
    all_words = words.all()

    # Join all words
    " ".join(all_words)


def demonstrate_list_collection():
    """Demonstrate Collection[List[int]] usage."""

    # Type-annotated list collection
    matrix: Collection[list[int]] = Collection([[1, 2, 3], [4, 5, 6]])

    # Append more lists
    matrix.append([7, 8, 9])

    # Get the first row (type checker knows it's a List[int])
    matrix.first()

    # Sum each row
    [sum(row) for row in matrix.all()]


def demonstrate_dict_collection():
    """Demonstrate Collection[Dict] usage."""

    # Type-annotated dict collection
    people: Collection[dict[str, any]] = Collection(
        [
            {"name": "Alice", "age": 25, "city": "New York"},
            {"name": "Bob", "age": 30, "city": "San Francisco"},
        ]
    )

    # Append more dictionaries
    people.append({"name": "Charlie", "age": 35, "city": "Chicago"})

    # Get the first person (type checker knows it's a Dict)
    people.first()

    # Extract all names
    [person["name"] for person in people.all()]


def demonstrate_custom_class_collection():
    """Demonstrate Collection[CustomClass] usage."""

    class Product:
        def __init__(self, name: str, price: float, category: str):
            self.name = name
            self.price = price
            self.category = category

        def __str__(self):
            return f"{self.name} (${self.price:.2f})"

    # Type-annotated custom class collection
    products: Collection[Product] = Collection(
        [
            Product("Laptop", 999.99, "Electronics"),
            Product("Book", 19.99, "Books"),
            Product("Coffee", 4.50, "Food"),
        ]
    )

    # Append more products
    products.append(Product("Headphones", 89.99, "Electronics"))

    # Get the first product (type checker knows it's a Product)
    products.first()

    # Calculate total value
    sum(product.price for product in products.all())


def demonstrate_optional_collection():
    """Demonstrate Collection[Optional[T]] usage."""

    # Type-annotated optional collection
    nullable_numbers: Collection[int | None] = Collection([1, None, 3, None, 5])

    # Append more values
    nullable_numbers.append(7)
    nullable_numbers.append(None)

    # Get the first value (type checker knows it's Optional[int])
    nullable_numbers.first()

    # Filter out None values
    [num for num in nullable_numbers.all() if num is not None]


def demonstrate_generic_function():
    """Demonstrate generic function usage with Collection."""

    def process_collection(collection: Collection[T]) -> list[T]:
        """Generic function that works with any Collection type."""
        items = collection.all()
        # Double the collection size by duplicating items
        return items + items

    # Use with int collection
    int_coll: Collection[int] = Collection([1, 2, 3])
    process_collection(int_coll)

    # Use with string collection
    str_coll: Collection[str] = Collection(["a", "b", "c"])
    process_collection(str_coll)


def demonstrate_pydantic_collection():
    """Demonstrate Collection[PydanticModel] usage."""

    try:
        from typing import List as PydanticList

        from pydantic import BaseModel

        class Product(BaseModel):
            id: int
            name: str
            price: float
            category: str
            in_stock: bool = True

        class Order(BaseModel):
            order_id: str
            customer_name: str
            products: list[Product]
            total_amount: float

        # Type-annotated Pydantic model collection
        products: Collection[Product] = Collection(
            [
                Product(id=1, name="Laptop", price=999.99, category="Electronics"),
                Product(
                    id=2, name="Book", price=19.99, category="Books", in_stock=False
                ),
                Product(id=3, name="Coffee", price=4.50, category="Food"),
            ]
        )

        # Append more products
        products.append(
            Product(id=4, name="Headphones", price=89.99, category="Electronics")
        )

        # Get the first product (type checker knows it's a Product)
        products.first()

        # Calculate total value
        sum(product.price for product in products.all())

        # Create orders with products
        orders: Collection[Order] = Collection(
            [
                Order(
                    order_id="ORD-001",
                    customer_name="Alice Johnson",
                    products=[products.all()[0], products.all()[2]],
                    total_amount=1004.49,
                ),
                Order(
                    order_id="ORD-002",
                    customer_name="Bob Smith",
                    products=[products.all()[3]],
                    total_amount=89.99,
                ),
            ]
        )

        # Get first order
        first_order = orders.first()

        # Serialize to JSON
        first_order.model_dump()

    except ImportError:
        pass


def main():
    """Run all demonstrations."""

    demonstrate_int_collection()
    demonstrate_str_collection()
    demonstrate_list_collection()
    demonstrate_dict_collection()
    demonstrate_custom_class_collection()
    demonstrate_optional_collection()
    demonstrate_generic_function()
    demonstrate_pydantic_collection()


if __name__ == "__main__":
    main()
