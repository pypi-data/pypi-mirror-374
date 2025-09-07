import pytest

from py_collections.collection import Collection


class TestRemoveOne:
    def test_remove_one_element(self):
        """Test removing the first occurrence of an element."""
        collection = Collection([1, 2, 2, 3, 4])
        collection.remove_one(2)
        assert collection.all() == [1, 2, 3, 4]

    def test_remove_one_with_predicate(self):
        """Test removing the first element that matches a predicate."""
        collection = Collection([1, 2, 2, 3, 4])
        collection.remove_one(lambda x: x == 2)
        assert collection.all() == [1, 2, 3, 4]

    def test_remove_one_element_not_found(self):
        """Test removing an element that doesn't exist."""
        collection = Collection([1, 2, 3])
        collection.remove_one(99)
        assert collection.all() == [1, 2, 3]

    def test_remove_one_predicate_no_match(self):
        """Test removing with a predicate that doesn't match any element."""
        collection = Collection([1, 2, 3])
        collection.remove_one(lambda x: x > 10)
        assert collection.all() == [1, 2, 3]

    def test_remove_one_empty_collection(self):
        """Test removing from an empty collection."""
        collection = Collection()
        collection.remove_one(1)
        assert collection.all() == []

    def test_remove_one_single_element(self):
        """Test removing from a collection with a single element."""
        collection = Collection([42])
        collection.remove_one(42)
        assert collection.all() == []

    def test_remove_one_first_element(self):
        """Test removing the first element."""
        collection = Collection([1, 2, 3])
        collection.remove_one(1)
        assert collection.all() == [2, 3]

    def test_remove_one_last_element(self):
        """Test removing the last element."""
        collection = Collection([1, 2, 3])
        collection.remove_one(3)
        assert collection.all() == [1, 2]

    def test_remove_one_middle_element(self):
        """Test removing an element from the middle."""
        collection = Collection([1, 2, 3, 4, 5])
        collection.remove_one(3)
        assert collection.all() == [1, 2, 4, 5]

    def test_remove_one_with_strings(self):
        """Test removing string elements."""
        collection = Collection(["a", "b", "a", "c", "a"])
        collection.remove_one("a")
        assert collection.all() == ["b", "a", "c", "a"]

    def test_remove_one_with_mixed_types(self):
        """Test removing with mixed types."""
        collection = Collection([1, "hello", 2, "world", 3])
        collection.remove_one("hello")
        assert collection.all() == [1, 2, "world", 3]

    def test_remove_one_with_none_values(self):
        """Test removing None values."""
        collection = Collection([1, None, 2, None, 3])
        collection.remove_one(None)
        assert collection.all() == [1, 2, None, 3]

    def test_remove_one_with_complex_objects(self):
        """Test removing complex objects."""
        collection = Collection([{"a": 1}, {"b": 2}, {"a": 1}, {"c": 3}])
        collection.remove_one({"a": 1})
        assert collection.all() == [{"b": 2}, {"a": 1}, {"c": 3}]

    def test_remove_one_modifies_collection(self):
        """Test that remove_one modifies the collection in-place."""
        collection = Collection([1, 2, 2, 3])
        original_id = id(collection._items)
        collection.remove_one(2)

        # The collection should be modified in-place
        assert collection.all() == [1, 2, 3]
        # The internal list should be the same object (modified)
        assert id(collection._items) == original_id

    def test_remove_one_chaining(self):
        """Test chaining remove_one with other methods."""
        collection = Collection([1, 2, 3, 4, 5, 6])

        # Remove first even number and then get first
        collection.remove_one(lambda x: x % 2 == 0)
        result = collection.first()
        assert result == 1

        # Remove first number > 3 and then reverse
        collection.remove_one(lambda x: x > 3)
        result = collection.reverse()
        assert result.all() == [6, 5, 3, 1]

    def test_remove_one_modifies_original(self):
        """Test that remove_one modifies the original collection."""
        original_items = [1, 2, 2, 3, 4]
        collection = Collection(original_items)

        collection.remove_one(2)

        # Original collection should be modified
        assert collection.all() == [1, 2, 3, 4]

    def test_remove_one_with_complex_predicate(self):
        """Test removing with a complex predicate."""
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        collection.remove_one(lambda x: x % 2 == 0)  # Remove first even number
        assert collection.all() == [1, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_remove_one_multiple_operations(self):
        """Test multiple remove_one operations."""
        collection = Collection([1, 2, 2, 3, 2, 4])

        # Remove first 2
        collection.remove_one(2)
        assert collection.all() == [1, 2, 3, 2, 4]

        # Remove second 2
        collection.remove_one(2)
        assert collection.all() == [1, 3, 2, 4]

        # Remove third 2
        collection.remove_one(2)
        assert collection.all() == [1, 3, 4]

    def test_remove_one_vs_remove_comparison(self):
        """Test the difference between remove_one and remove."""
        collection1 = Collection([1, 2, 2, 3, 2, 4])
        collection2 = Collection([1, 2, 2, 3, 2, 4])

        # remove_one removes only the first occurrence
        collection1.remove_one(2)
        assert collection1.all() == [1, 2, 3, 2, 4]

        # remove removes all occurrences
        collection2.remove(2)
        assert collection2.all() == [1, 3, 4]
