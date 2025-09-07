#!/usr/bin/env python3
"""
Example demonstrating the map method of the Collection class.

The map method applies a function to every item in the collection and returns
a new collection with the transformed items.
"""

from py_collections import Collection


def main():
    print("=== Collection.map() Method Examples ===\n")

    # Create sample collections
    numbers = Collection([1, 2, 3, 4, 5])
    strings = Collection(["hello", "world", "python"])
    mixed = Collection([1, "two", 3.0, True, None])

    print("Original collections:")
    print(f"  Numbers: {numbers}")
    print(f"  Strings: {strings}")
    print(f"  Mixed: {mixed}\n")

    # Example 1: Basic mathematical transformations
    print("1. Basic mathematical transformations:")
    doubled = numbers.map(lambda x: x * 2)
    squared = numbers.map(lambda x: x**2)
    plus_one = numbers.map(lambda x: x + 1)

    print(f"   numbers.map(lambda x: x * 2).all() => {doubled.all()}")
    print(f"   numbers.map(lambda x: x ** 2).all() => {squared.all()}")
    print(f"   numbers.map(lambda x: x + 1).all() => {plus_one.all()}")
    print()

    # Example 2: Type conversions
    print("2. Type conversions:")
    to_strings = numbers.map(str)
    to_floats = numbers.map(float)
    to_booleans = numbers.map(bool)

    print(f"   numbers.map(str).all() => {to_strings.all()}")
    print(f"   numbers.map(float).all() => {to_floats.all()}")
    print(f"   numbers.map(bool).all() => {to_booleans.all()}")
    print()

    # Example 3: String operations
    print("3. String operations:")
    uppercase = strings.map(str.upper)
    lengths = strings.map(len)
    reversed_strings = strings.map(lambda s: s[::-1])

    print(f"   strings.map(str.upper).all() => {uppercase.all()}")
    print(f"   strings.map(len).all() => {lengths.all()}")
    print(f"   strings.map(lambda s: s[::-1]).all() => {reversed_strings.all()}")
    print()

    # Example 4: Conditional transformations
    print("4. Conditional transformations:")
    even_odd = numbers.map(lambda x: "even" if x % 2 == 0 else "odd")
    positive_negative = numbers.map(
        lambda x: "positive" if x > 0 else "zero" if x == 0 else "negative"
    )

    print(
        f"   numbers.map(lambda x: 'even' if x % 2 == 0 else 'odd').all() => {even_odd.all()}"
    )
    print(
        f"   numbers.map(lambda x: 'positive' if x > 0 else 'zero' if x == 0 else 'negative').all() => {positive_negative.all()}"
    )
    print()

    # Example 5: Complex transformations
    print("5. Complex transformations:")
    complex_transform = numbers.map(
        lambda x: {"value": x, "doubled": x * 2, "squared": x**2}
    )
    formatted_numbers = numbers.map(lambda x: f"Number {x}: {x * 2}")

    print(f"   Complex transform (first item): {complex_transform.first()}")
    print(f"   Formatted numbers: {formatted_numbers.all()}")
    print()

    # Example 6: Working with None values
    print("6. Working with None values:")
    handle_none = mixed.map(lambda x: "None" if x is None else str(x))
    type_names = mixed.map(lambda x: type(x).__name__)

    print(
        f"   mixed.map(lambda x: 'None' if x is None else str(x)).all() => {handle_none.all()}"
    )
    print(f"   mixed.map(lambda x: type(x).__name__).all() => {type_names.all()}")
    print()

    # Example 7: Chaining map operations
    print("7. Chaining map operations:")
    chained = numbers.map(lambda x: x * 2).map(lambda x: x + 1).map(lambda x: x**2)
    print(
        f"   numbers.map(lambda x: x * 2).map(lambda x: x + 1).map(lambda x: x ** 2).all() => {chained.all()}"
    )
    print()

    # Example 8: Combining with other methods
    print("8. Combining with other methods:")
    filtered_and_mapped = numbers.filter(lambda x: x % 2 == 0).map(lambda x: x * 10)
    print(
        f"   numbers.filter(lambda x: x % 2 == 0).map(lambda x: x * 10).all() => {filtered_and_mapped.all()}"
    )
    print()

    # Example 9: Practical use cases
    print("9. Practical use cases:")

    # User data transformation
    users = Collection(
        [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35},
        ]
    )

    names = users.map(lambda user: user["name"])
    ages = users.map(lambda user: user["age"])
    greetings = users.map(lambda user: f"Hello, {user['name']}!")

    print(f"   Users: {users.all()}")
    print(f"   Names: {names.all()}")
    print(f"   Ages: {ages.all()}")
    print(f"   Greetings: {greetings.all()}")
    print()

    # Data processing
    temperatures = Collection([20, 25, 30, 35, 40])
    fahrenheit = temperatures.map(lambda c: (c * 9 / 5) + 32)
    status = temperatures.map(
        lambda c: "cold" if c < 25 else "warm" if c < 35 else "hot"
    )

    print(f"   Celsius: {temperatures.all()}")
    print(f"   Fahrenheit: {fahrenheit.all()}")
    print(f"   Status: {status.all()}")
    print()

    # Example 10: Original collection remains unchanged
    print("10. Original collection remains unchanged:")
    original_numbers = numbers.all()
    result = numbers.map(lambda x: x * 100)

    print(f"   Original: {original_numbers}")
    print(f"   Mapped result: {result.all()}")
    print(f"   Original unchanged: {numbers.all() == original_numbers}")
    print()

    print("=== End of Examples ===")


if __name__ == "__main__":
    main()
