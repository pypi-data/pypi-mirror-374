import pytest

from py_collections import Collection


class TestGroupBy:
    """Test cases for Collection group_by functionality."""

    def test_group_by_string_key_dict(self):
        """Test grouping by string key with dictionary items."""
        users = Collection(
            [
                {"name": "Alice", "department": "Engineering", "age": 25},
                {"name": "Bob", "department": "Sales", "age": 30},
                {"name": "Charlie", "department": "Engineering", "age": 35},
                {"name": "Diana", "department": "Marketing", "age": 28},
                {"name": "Eve", "department": "Engineering", "age": 32},
            ]
        )

        grouped = users.group_by("department")

        assert len(grouped) == 3
        assert "Engineering" in grouped
        assert "Sales" in grouped
        assert "Marketing" in grouped

        assert len(grouped["Engineering"]) == 3
        assert len(grouped["Sales"]) == 1
        assert len(grouped["Marketing"]) == 1

        # Check that items are correctly grouped
        engineering_names = [user["name"] for user in grouped["Engineering"].all()]
        assert "Alice" in engineering_names
        assert "Charlie" in engineering_names
        assert "Eve" in engineering_names

    def test_group_by_string_key_object(self):
        """Test grouping by string key with object items."""

        class User:
            def __init__(self, name: str, department: str, age: int):
                self.name = name
                self.department = department
                self.age = age

            def __repr__(self):
                return f"User({self.name}, {self.department}, {self.age})"

        users = Collection(
            [
                User("Alice", "Engineering", 25),
                User("Bob", "Sales", 30),
                User("Charlie", "Engineering", 35),
                User("Diana", "Marketing", 28),
            ]
        )

        grouped = users.group_by("department")

        assert len(grouped) == 3
        assert "Engineering" in grouped
        assert "Sales" in grouped
        assert "Marketing" in grouped

        assert len(grouped["Engineering"]) == 2
        assert len(grouped["Sales"]) == 1
        assert len(grouped["Marketing"]) == 1

    def test_group_by_callable(self):
        """Test grouping by callable function."""
        numbers = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Group by even/odd
        grouped = numbers.group_by(lambda x: "even" if x % 2 == 0 else "odd")

        assert len(grouped) == 2
        assert "even" in grouped
        assert "odd" in grouped

        assert len(grouped["even"]) == 5
        assert len(grouped["odd"]) == 5

        # Check that items are correctly grouped
        even_numbers = grouped["even"].all()
        odd_numbers = grouped["odd"].all()

        assert all(x % 2 == 0 for x in even_numbers)
        assert all(x % 2 == 1 for x in odd_numbers)

    def test_group_by_callable_complex(self):
        """Test grouping by complex callable function."""
        users = Collection(
            [
                {"name": "Alice", "age": 25},
                {"name": "Bob", "age": 30},
                {"name": "Charlie", "age": 35},
                {"name": "Diana", "age": 28},
                {"name": "Eve", "age": 42},
            ]
        )

        # Group by age decade
        grouped = users.group_by(lambda user: (user["age"] // 10) * 10)

        assert len(grouped) == 3
        assert 20 in grouped  # 25, 28
        assert 30 in grouped  # 30, 35
        assert 40 in grouped  # 42

        assert len(grouped[20]) == 2
        assert len(grouped[30]) == 2
        assert len(grouped[40]) == 1

    def test_group_by_none(self):
        """Test grouping by item itself (key=None)."""
        numbers = Collection([1, 2, 2, 3, 3, 3, 4, 4, 4, 4])

        grouped = numbers.group_by()

        assert len(grouped) == 4
        assert 1 in grouped
        assert 2 in grouped
        assert 3 in grouped
        assert 4 in grouped

        assert len(grouped[1]) == 1
        assert len(grouped[2]) == 2
        assert len(grouped[3]) == 3
        assert len(grouped[4]) == 4

    def test_group_by_strings(self):
        """Test grouping by string items."""
        words = Collection(["apple", "banana", "apple", "cherry", "banana", "date"])

        grouped = words.group_by()

        assert len(grouped) == 4
        assert "apple" in grouped
        assert "banana" in grouped
        assert "cherry" in grouped
        assert "date" in grouped

        assert len(grouped["apple"]) == 2
        assert len(grouped["banana"]) == 2
        assert len(grouped["cherry"]) == 1
        assert len(grouped["date"]) == 1

    def test_group_by_empty_collection(self):
        """Test grouping empty collection."""
        empty = Collection()

        grouped = empty.group_by("department")

        assert grouped == {}

    def test_group_by_missing_key(self):
        """Test grouping by missing key."""
        users = Collection([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])

        grouped = users.group_by("department")

        # Missing keys should be grouped under None
        assert None in grouped
        assert len(grouped[None]) == 2

    def test_group_by_missing_attribute(self):
        """Test grouping by missing object attribute."""

        class User:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

        users = Collection([User("Alice", 25), User("Bob", 30)])

        grouped = users.group_by("department")

        # Missing attributes should be grouped under None
        assert None in grouped
        assert len(grouped[None]) == 2

    def test_group_by_non_hashable_keys(self):
        """Test grouping with non-hashable keys (lists, dicts)."""
        items = Collection(
            [
                {"id": 1, "tags": ["red", "blue"]},
                {"id": 2, "tags": ["red", "green"]},
                {"id": 3, "tags": ["blue", "green"]},
            ]
        )

        grouped = items.group_by("tags")

        # Non-hashable keys should be converted to strings
        assert "['red', 'blue']" in grouped
        assert "['red', 'green']" in grouped
        assert "['blue', 'green']" in grouped

        assert len(grouped["['red', 'blue']"]) == 1
        assert len(grouped["['red', 'green']"]) == 1
        assert len(grouped["['blue', 'green']"]) == 1

    def test_group_by_invalid_key_type(self):
        """Test grouping with invalid key type."""
        collection = Collection([1, 2, 3])

        with pytest.raises(ValueError, match="Key must be a string, callable, or None"):
            collection.group_by(123)

    def test_group_by_multiple_criteria(self):
        """Test grouping by multiple criteria using callable."""
        users = Collection(
            [
                {"name": "Alice", "age": 25, "city": "NYC"},
                {"name": "Bob", "age": 30, "city": "LA"},
                {"name": "Charlie", "age": 25, "city": "NYC"},
                {"name": "Diana", "age": 30, "city": "LA"},
            ]
        )

        # Group by age and city combination
        grouped = users.group_by(lambda user: (user["age"], user["city"]))

        assert len(grouped) == 2
        assert (25, "NYC") in grouped
        assert (30, "LA") in grouped

        assert len(grouped[(25, "NYC")]) == 2
        assert len(grouped[(30, "LA")]) == 2

    def test_group_by_case_sensitive(self):
        """Test that grouping is case sensitive."""
        words = Collection(["Apple", "apple", "APPLE", "Banana"])

        grouped = words.group_by()

        assert len(grouped) == 4
        assert "Apple" in grouped
        assert "apple" in grouped
        assert "APPLE" in grouped
        assert "Banana" in grouped

        assert len(grouped["Apple"]) == 1
        assert len(grouped["apple"]) == 1
        assert len(grouped["APPLE"]) == 1
        assert len(grouped["Banana"]) == 1

    def test_group_by_return_collection_instances(self):
        """Test that grouped values are Collection instances."""
        numbers = Collection([1, 2, 3, 4, 5])

        grouped = numbers.group_by(lambda x: "even" if x % 2 == 0 else "odd")

        assert isinstance(grouped["even"], Collection)
        assert isinstance(grouped["odd"], Collection)

        # Test that grouped collections have the same methods
        assert hasattr(grouped["even"], "filter")
        assert hasattr(grouped["even"], "first")
        assert hasattr(grouped["even"], "all")
