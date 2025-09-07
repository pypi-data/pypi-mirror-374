#!/usr/bin/env python3
"""
Example demonstrating the pluck method of the Collection class.

The pluck method extracts values from a collection of items based on a key or attribute,
inspired by Laravel's pluck method: https://laravel.com/docs/12.x/collections#method-pluck
"""

from py_collections import Collection


def main():
    print("=== Collection.pluck() Method Examples ===\n")

    # Create sample collections
    users = Collection(
        [
            {"name": "Alice", "age": 25, "city": "New York", "active": True},
            {"name": "Bob", "age": 30, "city": "Los Angeles", "active": False},
            {"name": "Charlie", "age": 35, "city": "Chicago", "active": True},
            {"name": "Diana", "age": 28, "city": "Boston", "active": True},
        ]
    )

    products = Collection(
        [
            {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
            {"id": 2, "name": "Book", "price": 19.99, "category": "Books"},
            {"id": 3, "name": "Phone", "price": 699.99, "category": "Electronics"},
            {"id": 4, "name": "Pen", "price": 2.99, "category": "Office"},
        ]
    )

    print("Original collections:")
    print(f"  Users: {users}")
    print(f"  Products: {products}\n")

    # Example 1: Basic pluck - extract single values
    print("1. Basic pluck - extract single values:")
    names = users.pluck("name")
    ages = users.pluck("age")
    cities = users.pluck("city")

    print(f"   users.pluck('name').all() => {names.all()}")
    print(f"   users.pluck('age').all() => {ages.all()}")
    print(f"   users.pluck('city').all() => {cities.all()}")
    print()

    # Example 2: Pluck with value_key - create key-value pairs
    print("2. Pluck with value_key - create key-value pairs:")
    name_age_pairs = users.pluck("name", "age")
    name_city_pairs = users.pluck("name", "city")

    print(f"   users.pluck('name', 'age').all() => {name_age_pairs.all()}")
    print(f"   users.pluck('name', 'city').all() => {name_city_pairs.all()}")
    print()

    # Example 3: Working with objects
    print("3. Working with objects:")

    class User:
        def __init__(self, name, age, city, active):
            self.name = name
            self.age = age
            self.city = city
            self.active = active

    user_objects = Collection(
        [
            User("Alice", 25, "New York", True),
            User("Bob", 30, "Los Angeles", False),
            User("Charlie", 35, "Chicago", True),
        ]
    )

    object_names = user_objects.pluck("name")
    object_ages = user_objects.pluck("age")
    name_active_pairs = user_objects.pluck("name", "active")

    print(f"   user_objects.pluck('name').all() => {object_names.all()}")
    print(f"   user_objects.pluck('age').all() => {object_ages.all()}")
    print(f"   user_objects.pluck('name', 'active').all() => {name_active_pairs.all()}")
    print()

    # Example 4: Handling missing keys
    print("4. Handling missing keys:")
    missing_key = users.pluck("email")  # Key doesn't exist
    missing_value_key = users.pluck("name", "email")  # value_key doesn't exist

    print(f"   users.pluck('email').all() => {missing_key.all()}")
    print(f"   users.pluck('name', 'email').all() => {missing_value_key.all()}")
    print()

    # Example 5: Working with different data types
    print("5. Working with different data types:")
    prices = products.pluck("price")
    categories = products.pluck("category")
    ids = products.pluck("id")

    print(f"   products.pluck('price').all() => {prices.all()}")
    print(f"   products.pluck('category').all() => {categories.all()}")
    print(f"   products.pluck('id').all() => {ids.all()}")
    print()

    # Example 6: Chaining with other methods
    print("6. Chaining with other methods:")
    active_user_names = users.filter(lambda x: x["active"]).pluck("name")
    uppercase_names = users.pluck("name").map(str.upper)
    expensive_products = products.filter(lambda x: x["price"] > 500).pluck("name")

    print(
        f"   users.filter(lambda x: x['active']).pluck('name').all() => {active_user_names.all()}"
    )
    print(f"   users.pluck('name').map(str.upper).all() => {uppercase_names.all()}")
    print(
        f"   products.filter(lambda x: x['price'] > 500).pluck('name').all() => {expensive_products.all()}"
    )
    print()

    # Example 7: Practical use cases
    print("7. Practical use cases:")

    # User management
    active_users = users.filter(lambda x: x["active"]).pluck("name")
    user_age_stats = users.pluck("age")
    avg_age = sum(user_age_stats.all()) / len(user_age_stats.all())

    print(f"   Active users: {active_users.all()}")
    print(f"   User ages: {user_age_stats.all()}")
    print(f"   Average age: {avg_age:.1f}")
    print()

    # Product management
    electronics_products = products.filter(
        lambda x: x["category"] == "Electronics"
    ).pluck("name")
    product_prices = products.pluck("price")
    total_value = sum(product_prices.all())

    print(f"   Electronics products: {electronics_products.all()}")
    print(f"   Product prices: {product_prices.all()}")
    print(f"   Total inventory value: ${total_value:.2f}")
    print()

    # Example 8: Complex data structures
    print("8. Complex data structures:")

    complex_data = Collection(
        [
            {
                "user": {"name": "Alice", "id": 1},
                "orders": [{"id": 101, "amount": 50}, {"id": 102, "amount": 75}],
                "preferences": {"theme": "dark", "language": "en"},
            },
            {
                "user": {"name": "Bob", "id": 2},
                "orders": [{"id": 201, "amount": 100}],
                "preferences": {"theme": "light", "language": "es"},
            },
        ]
    )

    user_names = complex_data.pluck("user")
    themes = complex_data.pluck("preferences")

    print(f"   User objects: {user_names.all()}")
    print(f"   Preference objects: {themes.all()}")
    print()

    # Example 8.5: Nested key access with dot notation
    print("8.5. Nested key access with dot notation:")

    nested_users = Collection(
        [
            {
                "name": "Alice",
                "address": {"city": "New York", "country": "USA", "zip": "10001"},
                "profile": {"age": 25, "email": "alice@example.com"},
            },
            {
                "name": "Bob",
                "address": {"city": "Los Angeles", "country": "USA", "zip": "90210"},
                "profile": {"age": 30, "email": "bob@example.com"},
            },
            {
                "name": "Charlie",
                "address": {"city": "Chicago", "country": "USA", "zip": "60601"},
                "profile": {"age": 35, "email": "charlie@example.com"},
            },
        ]
    )

    cities = nested_users.pluck("address.city")
    countries = nested_users.pluck("address.country")
    emails = nested_users.pluck("profile.email")
    ages = nested_users.pluck("profile.age")

    print(f"   Cities: {cities.all()}")
    print(f"   Countries: {countries.all()}")
    print(f"   Emails: {emails.all()}")
    print(f"   Ages: {ages.all()}")
    print()

    # Example 8.6: Deeply nested access
    print("8.6. Deeply nested access:")

    deeply_nested = Collection(
        [
            {
                "user": {
                    "profile": {
                        "contact": {
                            "email": "alice@example.com",
                            "phone": {"mobile": "555-0101", "work": "555-0102"},
                        }
                    }
                }
            },
            {
                "user": {
                    "profile": {
                        "contact": {
                            "email": "bob@example.com",
                            "phone": {"mobile": "555-0201", "work": "555-0202"},
                        }
                    }
                }
            },
        ]
    )

    emails_deep = deeply_nested.pluck("user.profile.contact.email")
    mobile_phones = deeply_nested.pluck("user.profile.contact.phone.mobile")

    print(f"   Deep emails: {emails_deep.all()}")
    print(f"   Mobile phones: {mobile_phones.all()}")
    print()

    # Example 8.7: Nested keys with value_key
    print("8.7. Nested keys with value_key:")

    name_city_pairs = nested_users.pluck("name", "address.city")
    city_country_pairs = nested_users.pluck("address.city", "address.country")
    name_email_pairs = nested_users.pluck("name", "profile.email")

    print(f"   Name-City pairs: {name_city_pairs.all()}")
    print(f"   City-Country pairs: {city_country_pairs.all()}")
    print(f"   Name-Email pairs: {name_email_pairs.all()}")
    print()

    # Example 9: Edge cases
    print("9. Edge cases:")

    # Empty collection
    empty_collection = Collection()
    empty_result = empty_collection.pluck("name")

    # Collection with None values
    mixed_data = Collection(
        [
            {"name": "Alice", "age": 25},
            {"name": None, "age": 30},
            {"name": "Charlie", "age": None},
        ]
    )
    mixed_names = mixed_data.pluck("name")
    mixed_ages = mixed_data.pluck("age")

    print(f"   Empty collection pluck: {empty_result.all()}")
    print(f"   Mixed data names: {mixed_names.all()}")
    print(f"   Mixed data ages: {mixed_ages.all()}")
    print()

    # Example 10: Original collection remains unchanged
    print("10. Original collection remains unchanged:")
    original_users = users.all()
    result = users.pluck("name")

    print(f"   Original: {original_users}")
    print(f"   Plucked result: {result.all()}")
    print(f"   Original unchanged: {users.all() == original_users}")
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
