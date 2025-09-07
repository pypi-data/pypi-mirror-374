from py_collections import Collection


class TestIteration:
    """Test cases for Collection iteration functionality."""

    def test_basic_iteration(self):
        """Test basic iteration over a collection."""
        items = [1, 2, 3, 4, 5]
        collection = Collection(items)

        # Test iteration in for loop
        result = []
        for item in collection:
            result.append(item)

        assert result == items

    def test_empty_collection_iteration(self):
        """Test iteration over an empty collection."""
        collection = Collection()

        # Should not raise any exception
        result = []
        for item in collection:
            result.append(item)

        assert result == []

    def test_iteration_with_different_types(self):
        """Test iteration with different data types."""
        items = ["hello", 42, True, [1, 2, 3], {"key": "value"}]
        collection = Collection(items)

        result = []
        for item in collection:
            result.append(item)

        assert result == items

    def test_iteration_preserves_order(self):
        """Test that iteration preserves the order of items."""
        items = [3, 1, 4, 1, 5, 9, 2, 6]
        collection = Collection(items)

        result = []
        for item in collection:
            result.append(item)

        assert result == items

    def test_multiple_iterations(self):
        """Test that multiple iterations work correctly."""
        items = [1, 2, 3]
        collection = Collection(items)

        # First iteration
        result1 = []
        for item in collection:
            result1.append(item)

        # Second iteration
        result2 = []
        for item in collection:
            result2.append(item)

        assert result1 == items
        assert result2 == items
        assert result1 == result2

    def test_iteration_with_append(self):
        """Test iteration after appending items."""
        collection = Collection([1, 2, 3])
        collection.append(4)
        collection.append(5)

        result = []
        for item in collection:
            result.append(item)

        assert result == [1, 2, 3, 4, 5]

    def test_list_comprehension(self):
        """Test using list comprehension with collection."""
        collection = Collection([1, 2, 3, 4, 5])

        # Double each number
        doubled = [item * 2 for item in collection]
        assert doubled == [2, 4, 6, 8, 10]

    def test_sum_with_iteration(self):
        """Test using sum() with collection iteration."""
        collection = Collection([1, 2, 3, 4, 5])

        total = sum(item for item in collection)
        assert total == 15

    def test_any_with_iteration(self):
        """Test using any() with collection iteration."""
        collection = Collection([1, 2, 3, 4, 5])

        has_even = any(item % 2 == 0 for item in collection)
        assert has_even is True

        has_negative = any(item < 0 for item in collection)
        assert has_negative is False

    def test_all_with_iteration(self):
        """Test using all() with collection iteration."""
        collection = Collection([2, 4, 6, 8, 10])

        all_even = all(item % 2 == 0 for item in collection)
        assert all_even is True

        all_positive = all(item > 0 for item in collection)
        assert all_positive is True

    def test_enumerate_with_iteration(self):
        """Test using enumerate() with collection iteration."""
        collection = Collection(["a", "b", "c"])

        enumerated = list(enumerate(collection))
        assert enumerated == [(0, "a"), (1, "b"), (2, "c")]
