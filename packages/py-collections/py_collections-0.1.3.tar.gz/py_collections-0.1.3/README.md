# py-collections

A Python collections library providing enhanced collection types with additional functionality, built using a modular mixin architecture.

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and Python environment management.

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed
- [taskipy](https://github.com/taskipy/taskipy) (optional, for easier command execution)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Install the package in development mode (for running examples):
   ```bash
   uv pip install -e .
   ```

4. (Optional) Install taskipy globally for easier command execution:
   ```bash
   pip install taskipy
   ```

### Running Tests

To run all tests:
```bash
uv run pytest
```

To run tests with verbose output:
```bash
uv run pytest -v
```

To run tests with coverage:
```bash
uv run pytest --cov=src/py_collections --cov-report=term-missing
```

To generate HTML coverage report:
```bash
uv run pytest --cov=src/py_collections --cov-report=html --cov-report=term-missing
```

To run a specific test file:
```bash
uv run pytest tests/core/test_init.py
```

To run tests for a specific mixin:
```bash
uv run pytest tests/mixins/basic_operations/
uv run pytest tests/mixins/transformation/
```

To run tests in watch mode (re-runs on file changes):
```bash
uv run pytest --watch
```

### Development Commands

#### Using taskipy (recommended)
If you have taskipy installed globally (`pip install taskipy`):
- **Install dev dependencies**: `uv sync --group dev`
- **Run linting**: `task check`
- **Format code**: `task format`
- **Check formatting**: `task format-check`
- **Auto-fix linting issues**: `task check-fix`
- **Run tests**: `task test`
- **Run tests with verbose output**: `task test-verbose`
- **Run tests with coverage**: `task test-coverage`
- **Run tests with HTML coverage report**: `task test-coverage-html`
- **Run all checks**: `task lint`
- **Run linting, formatting, and tests**: `task all`

If you don't have taskipy installed globally, use:
- **Run linting**: `uv run python -c "from taskipy import cli; cli.main()" check`
- **Format code**: `uv run python -c "from taskipy import cli; cli.main()" format`
- **Check formatting**: `uv run python -c "from taskipy import cli; cli.main()" format-check`
- **Auto-fix linting issues**: `uv run python -c "from taskipy import cli; cli.main()" check-fix`
- **Run tests**: `uv run python -c "from taskipy import cli; cli.main()" test`
- **Run tests with verbose output**: `uv run python -c "from taskipy import cli; cli.main()" test-verbose`
- **Run tests with coverage**: `uv run python -c "from taskipy import cli; cli.main()" test-coverage`
- **Run tests with HTML coverage report**: `uv run python -c "from taskipy import cli; cli.main()" test-coverage-html`
- **Run all checks**: `uv run python -c "from taskipy import cli; cli.main()" lint`
- **Run linting, formatting, and tests**: `uv run python -c "from taskipy import cli; cli.main()" all`

#### Using uv directly
- **Run linting**: `uv run ruff check .`
- **Format code**: `uv run ruff format .`
- **Type checking**: `uv run mypy src/`
- **Run all checks**: `uv run ruff check . && uv run ruff format --check .`

## Project Structure

```
py-collections/
├── src/py_collections/     # Main package source code
│   ├── collection.py       # Main Collection class (combines all mixins)
│   ├── collection_map.py   # CollectionMap class
│   └── mixins/            # Modular mixin classes
│       ├── basic_operations.py    # append, extend, all, len, iteration
│       ├── element_access.py     # first, last, exists, first_or_raise
│       ├── navigation.py         # after, before
│       ├── transformation.py    # map, pluck, filter, reverse, clone
│       ├── grouping.py          # group_by, chunk
│       ├── removal.py           # remove, remove_one
│       └── utility.py           # take, dump_me, dump_me_and_die
├── tests/                  # Test files organized by functionality
│   ├── core/              # Core Collection tests
│   ├── collection_map/    # CollectionMap tests
│   └── mixins/           # Tests organized by mixin
│       ├── basic_operations/
│       ├── element_access/
│       ├── navigation/
│       ├── transformation/
│       ├── grouping/
│       ├── removal/
│       └── utility/
├── examples/               # Example usage and demonstrations
├── pyproject.toml         # Project configuration and dependencies
└── README.md              # This file
```

## Architecture

The library uses a **mixin-based architecture** to provide modular, maintainable code:

### Mixin Classes

Each mixin provides a focused set of related functionality:

- **BasicOperationsMixin**: Core collection operations (append, extend, all, len, iteration)
- **ElementAccessMixin**: Element retrieval and existence checking (first, last, exists, first_or_raise)
- **NavigationMixin**: Relative element access (after, before)
- **TransformationMixin**: Data transformation operations (map, pluck, filter, reverse, clone)
- **GroupingMixin**: Data grouping and chunking (group_by, chunk)
- **RemovalMixin**: Element removal operations (remove, remove_one)
- **UtilityMixin**: Utility and debugging methods (take, dump_me, dump_me_and_die)

### Benefits of This Architecture

1. **Modularity**: Each mixin focuses on a specific domain of functionality
2. **Maintainability**: Changes to one area don't affect others
3. **Testability**: Tests are organized by functionality
4. **Extensibility**: New functionality can be added as new mixins
5. **Reusability**: Mixins can be used independently if needed

## Features

- Enhanced collection types with additional utility methods
- **Modular mixin architecture** for maintainable code
- Type-safe implementations with full generic support
- **100% test coverage** - All code paths tested
- Modern Python features (3.13+)
- Specialized `CollectionMap` for working with grouped data
- Code quality tools: Ruff (linting + formatting), MyPy (type checking)

## Available Methods

The `Collection` class provides the following methods, organized by mixin:

### Basic Operations (BasicOperationsMixin)
- `append(item)` - Add an item to the collection
- `extend(items)` - Add multiple items from a list or another collection
- `all()` - Get all items as a list
- `len()` - Get the number of items
- **Iteration** - Use in `for` loops and with built-in functions like `sum()`, `max()`, `min()`, `any()`, `all()`, etc.

### Element Access (ElementAccessMixin)
- `first(predicate=None)` - Get the first element (optionally matching a predicate)
- `first_or_raise(predicate=None)` - Get the first element or raise exception if not found
- `last()` - Get the last element
- `exists(predicate=None)` - Check if an element exists (returns boolean)

### Navigation (NavigationMixin)
- `after(target)` - Get the element after a target element or predicate match
- `before(target)` - Get the element before a target element or predicate match

### Transformation (TransformationMixin)
- `filter(predicate)` - Filter elements based on a predicate
- `map(func)` - Apply a function to every item and return a new collection with the results
- `pluck(key, value_key=None)` - Extract values from items based on a key or attribute (inspired by Laravel)
- `reverse()` - Return a new collection with items in reverse order
- `clone()` - Return a new collection with the same items

### Grouping (GroupingMixin)
- `group_by(key)` - Group items by a key or callback function
- `chunk(size)` - Split collection into smaller chunks

### Removal (RemovalMixin)
- `remove(target)` - Remove all items that match the target element or predicate (modifies collection in-place)
- `remove_one(target)` - Remove the first occurrence of an item that matches the target element or predicate (modifies collection in-place)

### Utility (UtilityMixin)
- `take(count)` - Return a new collection with the specified number of items (positive: from beginning, negative: from end)
- `dump_me()` - Debug method to print collection contents (doesn't stop execution)
- `dump_me_and_die()` - Debug method to print collection contents and stop execution
- `to_dict(mode=None)` - Convert items to plain Python structures. With `mode="json"`, ensures JSON-serializable output (datetimes to ISO strings, Decimals to floats, UUIDs to strings, sets to lists, and dict keys to strings)
- `to_json()` - Return a JSON string using `to_dict(mode="json")`

### CollectionMap Class
A specialized map that stores `Collection` instances as values, providing convenient methods for working with grouped data:
- Dictionary-like interface with string keys and Collection values
- Automatic conversion of lists/items to Collection instances
- `get(key)` - Returns empty Collection if key doesn't exist (no KeyError)
- `add(key, items)` - Add items to existing key or create new key
- `flatten()` - Combine all collections into one
- `map(func)` - Apply function to each collection
- `filter(predicate)` - Filter collections based on criteria
- `filter_by_size(min_size, max_size)` - Filter by collection size
- `total_items()` - Get total count across all collections
- `largest_group()` / `smallest_group()` - Find groups by size
- `group_sizes()` - Get size of each group

### Usage Examples

```python
from py_collections import Collection

# Basic usage
numbers = Collection([1, 2, 3, 4, 5])
numbers.append(6)

# Extending with multiple items
numbers.extend([7, 8, 9])
other_numbers = Collection([10, 11, 12])
numbers.extend(other_numbers)

# Reversing the collection
reversed_numbers = numbers.reverse()

# Cloning the collection
cloned_numbers = numbers.clone()  # Create a copy with the same items

# Taking items from the collection
first_two = numbers.take(2)  # Take first 2 items
last_three = numbers.take(-3)  # Take last 3 items

# Mapping elements
doubled = numbers.map(lambda x: x * 2)  # Double each number
squared = numbers.map(lambda x: x ** 2)  # Square each number
strings = numbers.map(str)  # Convert to strings

# Plucking values from objects/dictionaries
users = Collection([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
names = users.pluck("name")  # ["Alice", "Bob"]
name_age_pairs = users.pluck("name", "age")  # [{"Alice": 25}, {"Bob": 30}]

# Nested key access with dot notation
nested_users = Collection([{"name": "Alice", "address": {"city": "NYC"}}, {"name": "Bob", "address": {"city": "LA"}}])
cities = nested_users.pluck("address.city")  # ["NYC", "LA"]
name_city_pairs = nested_users.pluck("name", "address.city")  # [{"Alice": "NYC"}, {"Bob": "LA"}]

# Removing elements
numbers.remove(1)  # Remove all occurrences of 1
numbers.remove(lambda x: x > 3)  # Remove all elements > 3
numbers.remove_one(lambda x: x == 2)  # Remove first occurrence of 2

# Check if elements exist
if numbers.exists(lambda x: x > 3):
    print("Found number greater than 3")

# Find elements
first_even = numbers.first(lambda x: x % 2 == 0)
after_three = numbers.after(3)

# Filter and chunk
evens = numbers.filter(lambda x: x % 2 == 0)
chunks = numbers.chunk(2)

# Group by
users = Collection([{"name": "Alice", "dept": "Eng"}, {"name": "Bob", "dept": "Sales"}])
by_dept = users.group_by("dept")
by_parity = numbers.group_by(lambda x: "even" if x % 2 == 0 else "odd")

# Iteration
for item in numbers:
    print(item)

# List comprehension
doubled = [item * 2 for item in numbers]

# Built-in functions
total = sum(item for item in numbers)
has_even = any(item % 2 == 0 for item in numbers)

# CollectionMap usage
# Serialization
from py_collections import Collection

data = Collection([
    {"name": "Alice", "age": 30},
    (1, 2, 3),
    {"tags": {"python", "collections"}},
])

# Plain Python structures
structure = data.to_dict()

# JSON-ready structure and JSON string
json_ready = data.to_dict(mode="json")
json_text = data.to_json()

### Pydantic Compatibility
If your items include Pydantic models, they are supported out of the box:

```python
from pydantic import BaseModel
from py_collections import Collection

class User(BaseModel):
    id: int
    name: str

users = Collection([User(id=1, name="Alice"), User(id=2, name="Bob")])

# Converts to list of dicts
users_dict = users.to_dict()

# JSON-ready and stringified
users_json_ready = users.to_dict(mode="json")
users_json = users.to_json()
```

from py_collections import CollectionMap

# Create from group_by result
grouped = users.group_by("department")
cmap = CollectionMap(grouped)

# Work with groups
engineering = cmap["Engineering"]
all_users = cmap.flatten()
group_stats = cmap.map(lambda c: len(c))

# Safe access and incremental building
missing = cmap.get("missing")  # Returns empty Collection
cmap.add("new_group", [1, 2, 3])  # Creates new group
cmap.add("existing_group", [4, 5])  # Extends existing group

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests: `uv run pytest`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
