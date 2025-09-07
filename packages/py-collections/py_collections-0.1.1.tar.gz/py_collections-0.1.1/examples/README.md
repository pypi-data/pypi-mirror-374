# Collection Examples

This folder contains examples demonstrating the usage of the `Collection` class from the `py_collections` package.

## Example Files

### `init_example.py`
Demonstrates Collection initialization methods:
- Initializing with an existing array
- Initializing an empty collection
- Collection independence (collections don't affect each other)

### `append_example.py`
Demonstrates the `append` method:
- Basic append functionality
- Appending different data types
- Appending to empty collections

### `first_last_example.py`
Demonstrates the `first` and `last` methods:
- Getting first and last elements
- Using predicates with `first` method to find elements that satisfy conditions
- Behavior after appending new elements
- Handling different data types
- Single element collections
- Error handling for empty collections

### `first_with_predicate_example.py`
Demonstrates the enhanced `first` method with predicate functions:
- Finding first elements that satisfy specific conditions
- Using lambda functions and custom predicates
- Working with different data types (numbers, strings, custom classes)
- Error handling when no element satisfies the predicate
- Complex predicate examples with custom classes

### `all_example.py`
Demonstrates the `all` method:
- Getting all items as a list
- Demonstrating that `all()` returns a copy
- Working with different data types
- Empty collection behavior

### `generic_types_example.py`
Demonstrates generic type usage:
- Typed collections (`Collection[int]`, `Collection[str]`, etc.)
- Custom class collections
- Mixed type collections
- Type safety demonstrations

### `edge_cases_example.py`
Demonstrates edge cases and error handling:
- Empty collection operations
- Single element collections
- Collections with `None` values
- Collections with empty containers
- Collection independence and deep copy behavior

### `comprehensive_example.py`
A comprehensive example that demonstrates all Collection methods together:
- Complete workflow from initialization to usage
- All methods in action
- Error handling
- String representation

### `typed_collections.py`
The original example file showing typed collections usage.

## Running the Examples

To run any example, navigate to the examples directory and execute:

```bash
python <example_file>.py
```

For example:
```bash
python init_example.py
python append_example.py
python comprehensive_example.py
```

## What Each Example Teaches

- **Initialization**: How to create collections with or without initial data
- **Appending**: How to add items to collections
- **Accessing**: How to get first, last, or all items
- **Filtering**: How to find first elements that satisfy conditions using predicates
- **Type Safety**: How to use generic types for better code safety
- **Error Handling**: How the collection behaves in edge cases
- **Best Practices**: How to use collections effectively in real scenarios

Each example is self-contained and can be run independently to understand specific functionality.
