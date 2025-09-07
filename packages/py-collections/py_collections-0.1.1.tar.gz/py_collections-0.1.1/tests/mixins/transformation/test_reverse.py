import pytest

from py_collections.collection import Collection


class TestReverse:
    def test_reverse_with_numbers(self):
        """Test reversing a collection of numbers."""
        collection = Collection([1, 2, 3, 4, 5])
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == [5, 4, 3, 2, 1]

    def test_reverse_with_strings(self):
        """Test reversing a collection of strings."""
        collection = Collection(["a", "b", "c", "d"])
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == ["d", "c", "b", "a"]

    def test_reverse_empty_collection(self):
        """Test reversing an empty collection."""
        collection = Collection()
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == []

    def test_reverse_single_item(self):
        """Test reversing a collection with a single item."""
        collection = Collection([42])
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == [42]

    def test_reverse_two_items(self):
        """Test reversing a collection with two items."""
        collection = Collection(["first", "second"])
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == ["second", "first"]

    def test_reverse_with_mixed_types(self):
        """Test reversing a collection with mixed types."""
        collection = Collection([1, "hello", True, None, 3.14])
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == [3.14, None, True, "hello", 1]

    def test_reverse_with_none_values(self):
        """Test reversing a collection with None values."""
        collection = Collection([1, None, 3, None, 5])
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == [5, None, 3, None, 1]

    def test_reverse_with_complex_objects(self):
        """Test reversing a collection with complex objects."""
        collection = Collection([{"a": 1}, {"b": 2}, {"c": 3}])
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == [{"c": 3}, {"b": 2}, {"a": 1}]

    def test_reverse_returns_new_collection(self):
        """Test that reverse returns a new collection, not the same one."""
        collection = Collection([1, 2, 3])
        reversed_collection = collection.reverse()

        # They should be different objects
        assert reversed_collection is not collection
        # Original should remain unchanged
        assert collection.all() == [1, 2, 3]
        # Reversed should have reversed order
        assert reversed_collection.all() == [3, 2, 1]

    def test_reverse_multiple_times(self):
        """Test reversing multiple times."""
        collection = Collection([1, 2, 3, 4])

        # First reverse
        reversed1 = collection.reverse()
        assert reversed1.all() == [4, 3, 2, 1]

        # Second reverse
        reversed2 = reversed1.reverse()
        assert reversed2.all() == [1, 2, 3, 4]

        # Third reverse
        reversed3 = reversed2.reverse()
        assert reversed3.all() == [4, 3, 2, 1]

    def test_reverse_with_duplicate_elements(self):
        """Test reversing a collection with duplicate elements."""
        collection = Collection([1, 2, 2, 3, 2, 4])
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == [4, 2, 3, 2, 2, 1]

    def test_reverse_with_large_collection(self):
        """Test reversing a larger collection."""
        collection = Collection(list(range(100)))
        reversed_collection = collection.reverse()
        assert reversed_collection.all() == list(range(99, -1, -1))

    def test_reverse_chaining(self):
        """Test chaining reverse with other methods."""
        collection = Collection([1, 2, 3, 4, 5, 6])

        # Reverse and then filter
        reversed_even = collection.reverse().filter(lambda x: x % 2 == 0)
        assert reversed_even.all() == [6, 4, 2]

        # Reverse and then get first
        first_after_reverse = collection.reverse().first()
        assert first_after_reverse == 6

    def test_reverse_preserves_original(self):
        """Test that reverse doesn't modify the original collection."""
        original_items = [1, 2, 3, 4, 5]
        collection = Collection(original_items)

        reversed_collection = collection.reverse()

        # Original collection should be unchanged
        assert collection.all() == original_items
        # Reversed collection should have reversed order
        assert reversed_collection.all() == [5, 4, 3, 2, 1]
