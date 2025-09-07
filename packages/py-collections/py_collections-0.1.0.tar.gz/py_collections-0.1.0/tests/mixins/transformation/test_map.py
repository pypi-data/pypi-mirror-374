import pytest

from py_collections import Collection


class TestMap:
    def test_map_basic_functionality(self):
        """Test basic map functionality with a simple transformation."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.map(lambda x: x * 2)
        assert result.all() == [2, 4, 6, 8, 10]
        assert isinstance(result, Collection)

    def test_map_with_string_conversion(self):
        """Test map with string conversion."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.map(str)
        assert result.all() == ["1", "2", "3", "4", "5"]
        assert isinstance(result, Collection)

    def test_map_with_square_function(self):
        """Test map with a square function."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.map(lambda x: x**2)
        assert result.all() == [1, 4, 9, 16, 25]
        assert isinstance(result, Collection)

    def test_map_with_strings(self):
        """Test map with string items."""
        collection = Collection(["hello", "world", "python"])
        result = collection.map(str.upper)
        assert result.all() == ["HELLO", "WORLD", "PYTHON"]
        assert isinstance(result, Collection)

    def test_map_with_string_length(self):
        """Test map with string length function."""
        collection = Collection(["hello", "world", "python"])
        result = collection.map(len)
        assert result.all() == [5, 5, 6]
        assert isinstance(result, Collection)

    def test_map_empty_collection(self):
        """Test map with empty collection."""
        collection = Collection()
        result = collection.map(lambda x: x * 2)
        assert result.all() == []
        assert isinstance(result, Collection)

    def test_map_with_mixed_types(self):
        """Test map with mixed type items."""
        collection = Collection([1, "two", 3.0, True])
        result = collection.map(type)
        expected_types = [int, str, float, bool]
        assert result.all() == expected_types
        assert isinstance(result, Collection)

    def test_map_with_none_values(self):
        """Test map with None values."""
        collection = Collection([1, None, 3, None, 5])
        result = collection.map(lambda x: "None" if x is None else str(x))
        assert result.all() == ["1", "None", "3", "None", "5"]
        assert isinstance(result, Collection)

    def test_map_with_complex_objects(self):
        """Test map with complex objects."""
        collection = Collection([{"name": "Alice"}, {"name": "Bob"}])
        result = collection.map(lambda x: x["name"])
        assert result.all() == ["Alice", "Bob"]
        assert isinstance(result, Collection)

    def test_map_with_conditional_logic(self):
        """Test map with conditional logic."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.map(lambda x: "even" if x % 2 == 0 else "odd")
        assert result.all() == ["odd", "even", "odd", "even", "odd"]
        assert isinstance(result, Collection)

    def test_map_with_multiple_operations(self):
        """Test map with multiple operations."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.map(lambda x: (x * 2) + 1)
        assert result.all() == [3, 5, 7, 9, 11]
        assert isinstance(result, Collection)

    def test_map_original_collection_unchanged(self):
        """Test that the original collection remains unchanged."""
        collection = Collection([1, 2, 3, 4, 5])
        original_items = collection.all()
        result = collection.map(lambda x: x * 2)

        # Verify result is correct
        assert result.all() == [2, 4, 6, 8, 10]

        # Verify original collection is unchanged
        assert collection.all() == original_items

    def test_map_returns_new_collection(self):
        """Test that map returns a new collection instance."""
        collection = Collection([1, 2, 3])
        result = collection.map(lambda x: x * 2)
        assert result is not collection
        assert result._items is not collection._items

    def test_map_with_custom_function(self):
        """Test map with a custom function."""

        def custom_func(x):
            return f"Item_{x}"

        collection = Collection([1, 2, 3])
        result = collection.map(custom_func)
        assert result.all() == ["Item_1", "Item_2", "Item_3"]
        assert isinstance(result, Collection)

    def test_map_with_builtin_functions(self):
        """Test map with built-in functions."""
        collection = Collection([1.5, 2.7, 3.2])
        result = collection.map(int)
        assert result.all() == [1, 2, 3]
        assert isinstance(result, Collection)

    def test_map_with_boolean_conversion(self):
        """Test map with boolean conversion."""
        collection = Collection([0, 1, "", "hello", None, True])
        result = collection.map(bool)
        assert result.all() == [False, True, False, True, False, True]
        assert isinstance(result, Collection)

    def test_map_chaining(self):
        """Test chaining map operations."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.map(lambda x: x * 2).map(lambda x: x + 1)
        assert result.all() == [3, 5, 7, 9, 11]
        assert isinstance(result, Collection)

    def test_map_with_lambda_and_filter(self):
        """Test map combined with filter."""
        collection = Collection([1, 2, 3, 4, 5, 6])
        result = collection.filter(lambda x: x % 2 == 0).map(lambda x: x * 2)
        assert result.all() == [4, 8, 12]
        assert isinstance(result, Collection)

    def test_map_with_error_handling(self):
        """Test map with functions that might raise errors."""
        collection = Collection([1, 2, 3, 4, 5])

        # This should work fine
        result = collection.map(lambda x: x / 2)
        assert result.all() == [0.5, 1.0, 1.5, 2.0, 2.5]

        # This should raise an error when trying to divide by zero
        with pytest.raises(ZeroDivisionError):
            collection.map(lambda x: 1 / (x - 3))  # Will fail on x=3

    def test_map_with_different_return_types(self):
        """Test map with functions that return different types."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.map(lambda x: {"value": x, "doubled": x * 2})
        expected = [
            {"value": 1, "doubled": 2},
            {"value": 2, "doubled": 4},
            {"value": 3, "doubled": 6},
            {"value": 4, "doubled": 8},
            {"value": 5, "doubled": 10},
        ]
        assert result.all() == expected
        assert isinstance(result, Collection)
