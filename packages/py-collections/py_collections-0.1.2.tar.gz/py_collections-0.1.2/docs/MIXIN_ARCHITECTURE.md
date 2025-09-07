# Mixin Architecture Documentation

This document explains the mixin-based architecture used in the py-collections library.

## Overview

The py-collections library uses a **mixin-based architecture** to provide modular, maintainable, and extensible code. Instead of having one large `Collection` class with all methods, the functionality is split into focused mixin classes that are combined to create the final `Collection` class.

## Architecture Benefits

### 1. Modularity
Each mixin focuses on a specific domain of functionality, making the code easier to understand and maintain.

### 2. Maintainability
Changes to one area of functionality don't affect other areas. For example, if you need to modify how `map()` works, you only need to look at the `TransformationMixin`.

### 3. Testability
Tests are organized by functionality, making it easier to find and maintain tests for specific features.

### 4. Extensibility
New functionality can be added by creating new mixins without modifying existing code.

### 5. Reusability
Mixins can potentially be used independently or in different combinations if needed.

## Mixin Classes

### BasicOperationsMixin
**Purpose**: Core collection operations and fundamental functionality.

**Methods**:
- `append(item)` - Add an item to the collection
- `extend(items)` - Add multiple items from a list or another collection
- `all()` - Get all items as a list
- `__len__()` - Get the number of items
- `__iter__()` - Enable iteration over the collection

**Key Features**:
- Handles basic list operations
- Manages the underlying `_items` list
- Provides iteration support

### ElementAccessMixin
**Purpose**: Element retrieval and existence checking.

**Methods**:
- `first(predicate=None)` - Get the first element (optionally matching a predicate)
- `first_or_raise(predicate=None)` - Get the first element or raise exception if not found
- `last()` - Get the last element
- `exists(predicate=None)` - Check if an element exists (returns boolean)
- `_find_first_index(predicate=None)` - Internal method to find first matching index

**Key Features**:
- Supports predicate-based element finding
- Provides both safe and exception-raising variants
- Includes the `ItemNotFoundException` exception

### NavigationMixin
**Purpose**: Relative element access within the collection.

**Methods**:
- `after(target)` - Get the element after a target element or predicate match
- `before(target)` - Get the element before a target element or predicate match

**Key Features**:
- Supports both element-based and predicate-based navigation
- Handles edge cases (first/last elements, missing targets)
- Returns `None` when no match is found

### TransformationMixin
**Purpose**: Data transformation and manipulation operations.

**Methods**:
- `map(func)` - Apply a function to every item and return a new collection with the results
- `pluck(key, value_key=None)` - Extract values from items based on a key or attribute
- `filter(predicate)` - Filter the collection based on a predicate function
- `reverse()` - Return a new collection with the items reversed in order
- `clone()` - Return a new collection with the same items

**Key Features**:
- All methods return new collections (immutable operations)
- Supports complex nested key access in `pluck()`
- Handles various data types and edge cases

### GroupingMixin
**Purpose**: Data grouping and chunking operations.

**Methods**:
- `group_by(key)` - Group the collection's items by a given key or callback function
- `chunk(size)` - Split the collection into smaller collections of the specified size

**Key Features**:
- Supports string keys, callable functions, and grouping by item itself
- Handles non-hashable keys by converting to strings
- Returns collections of collections for further processing

### RemovalMixin
**Purpose**: Element removal operations.

**Methods**:
- `remove(target)` - Remove all items that match the target element or predicate
- `remove_one(target)` - Remove the first occurrence of an item that matches the target element or predicate

**Key Features**:
- Modifies the collection in-place (mutable operations)
- Supports both element-based and predicate-based removal
- Handles edge cases gracefully

### UtilityMixin
**Purpose**: Utility and debugging methods.

**Methods**:
- `take(count)` - Return a new collection with the specified number of items
- `dump_me()` - Debug method to print collection contents (doesn't stop execution)
- `dump_me_and_die()` - Debug method to print collection contents and stop execution

**Key Features**:
- `take()` supports both positive and negative counts
- Debug methods provide detailed collection information
- Useful for development and troubleshooting

## How Mixins Work Together

### The Collection Class
The main `Collection` class inherits from all mixins:

```python
class Collection[T](
    BasicOperationsMixin,
    ElementAccessMixin,
    NavigationMixin,
    TransformationMixin,
    GroupingMixin,
    RemovalMixin,
    UtilityMixin,
):
    def __init__(self, items: list[T] | None = None):
        self._items = items.copy() if items is not None else []
```

### Shared State
All mixins share the `_items` attribute, which contains the underlying list of items. This is the only shared state between mixins.

### Method Resolution
Python's method resolution order (MRO) ensures that methods are found in the correct mixin. If multiple mixins define the same method name, the first one in the inheritance list takes precedence.

## Adding New Functionality

### Creating a New Mixin
To add new functionality:

1. Create a new mixin class in `src/py_collections/mixins/`
2. Add the mixin to the `Collection` class inheritance list
3. Update the `__init__.py` files to export the new mixin
4. Add tests in `tests/mixins/`

Example:
```python
# src/py_collections/mixins/sorting.py
class SortingMixin[T]:
    def sort(self, key=None, reverse=False) -> "Collection[T]":
        from ..collection import Collection
        sorted_items = sorted(self._items, key=key, reverse=reverse)
        return Collection(sorted_items)
```

### Modifying Existing Mixins
When modifying existing mixins:

1. Only change the specific mixin file
2. Update tests in the corresponding test directory
3. Ensure changes don't break other mixins
4. Update documentation if needed

## Testing Strategy

### Test Organization
Tests are organized to match the mixin structure:

```
tests/
├── core/                    # Core Collection functionality
├── collection_map/          # CollectionMap tests
└── mixins/                # Tests organized by mixin
    ├── basic_operations/
    ├── element_access/
    ├── navigation/
    ├── transformation/
    ├── grouping/
    ├── removal/
    └── utility/
```

### Test Principles
1. **Isolation**: Each mixin's tests focus only on that mixin's functionality
2. **Comprehensive**: Test all edge cases and error conditions
3. **Integration**: Core tests verify that mixins work together correctly
4. **Coverage**: Maintain 100% test coverage across all mixins

## Best Practices

### Mixin Design
1. **Single Responsibility**: Each mixin should have one clear purpose
2. **Minimal Dependencies**: Mixins should depend only on the `_items` attribute
3. **Consistent Interfaces**: Use consistent parameter names and return types
4. **Error Handling**: Handle edge cases gracefully within each mixin

### Code Organization
1. **Clear Separation**: Keep mixin functionality separate and focused
2. **Documentation**: Document each mixin's purpose and methods
3. **Type Hints**: Use proper type hints for all methods
4. **Examples**: Include usage examples in docstrings

### Testing
1. **Unit Tests**: Test each mixin in isolation
2. **Integration Tests**: Test how mixins work together
3. **Edge Cases**: Test boundary conditions and error cases
4. **Performance**: Consider performance implications of mixin combinations

## Future Extensions

The mixin architecture makes it easy to add new functionality:

### Potential New Mixins
- **SortingMixin**: Sort operations (sort, sort_by, etc.)
- **AggregationMixin**: Statistical operations (sum, average, min, max, etc.)
- **ValidationMixin**: Data validation and verification
- **SerializationMixin**: JSON, CSV, and other format support
- **CachingMixin**: Memoization and caching functionality

### Custom Collections
The mixin architecture also enables creating specialized collections by combining only the needed mixins:

```python
class SimpleCollection[T](
    BasicOperationsMixin,
    ElementAccessMixin,
):
    """A simplified collection with only basic operations."""
    pass

class ReadOnlyCollection[T](
    BasicOperationsMixin,
    ElementAccessMixin,
    NavigationMixin,
    TransformationMixin,
    GroupingMixin,
    UtilityMixin,
):
    """A read-only collection without removal operations."""
    pass
```

This architecture provides a solid foundation for building robust, maintainable, and extensible collection utilities.
