import pytest

from py_collections.collection import Collection


class TestRemove:
    def test_remove_element(self):
        """Test removing a specific element."""
        collection = Collection([1, 2, 2, 3, 4])
        collection.remove(1)
        assert collection.all() == [2, 2, 3, 4]

    def test_remove_all_occurrences(self):
        """Test removing all occurrences of an element."""
        collection = Collection([1, 2, 2, 3, 2, 4])
        collection.remove(2)
        assert collection.all() == [1, 3, 4]

    def test_remove_with_predicate(self):
        """Test removing elements with a predicate."""
        collection = Collection([1, 2, 2, 3, 4])
        collection.remove(lambda x: x > 3)
        assert collection.all() == [1, 2, 2, 3]

    def test_remove_with_complex_predicate(self):
        """Test removing elements with a complex predicate."""
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        collection.remove(lambda x: x % 2 == 0)  # Remove even numbers
        assert collection.all() == [1, 3, 5, 7, 9]

    def test_remove_element_not_found(self):
        """Test removing an element that doesn't exist."""
        collection = Collection([1, 2, 3])
        collection.remove(99)
        assert collection.all() == [1, 2, 3]

    def test_remove_predicate_no_match(self):
        """Test removing with a predicate that doesn't match any element."""
        collection = Collection([1, 2, 3])
        collection.remove(lambda x: x > 10)
        assert collection.all() == [1, 2, 3]

    def test_remove_empty_collection(self):
        """Test removing from an empty collection."""
        collection = Collection()
        collection.remove(1)
        assert collection.all() == []

    def test_remove_all_elements(self):
        """Test removing all elements."""
        collection = Collection([1, 1, 1])
        collection.remove(1)
        assert collection.all() == []

    def test_remove_with_strings(self):
        """Test removing string elements."""
        collection = Collection(["a", "b", "a", "c", "a"])
        collection.remove("a")
        assert collection.all() == ["b", "c"]

    def test_remove_with_mixed_types(self):
        """Test removing with mixed types."""
        collection = Collection([1, "hello", 2, "world", 3])
        collection.remove("hello")
        assert collection.all() == [1, 2, "world", 3]

    def test_remove_with_none_values(self):
        """Test removing None values."""
        collection = Collection([1, None, 2, None, 3])
        collection.remove(None)
        assert collection.all() == [1, 2, 3]

    def test_remove_with_complex_objects(self):
        """Test removing complex objects."""
        collection = Collection([{"a": 1}, {"b": 2}, {"a": 1}, {"c": 3}])
        collection.remove({"a": 1})
        assert collection.all() == [{"b": 2}, {"c": 3}]

    def test_remove_modifies_collection(self):
        """Test that remove modifies the collection in-place."""
        collection = Collection([1, 2, 3])
        original_id = id(collection._items)
        collection.remove(2)

        # The collection should be modified in-place
        assert collection.all() == [1, 3]
        # The internal list should be the same object (modified)
        assert id(collection._items) == original_id

    def test_remove_chaining(self):
        """Test chaining remove with other methods."""
        collection = Collection([1, 2, 3, 4, 5, 6])

        # Remove even numbers and then get first
        collection.remove(lambda x: x % 2 == 0)
        result = collection.first()
        assert result == 1

        # Remove numbers > 3 and then reverse
        collection.remove(lambda x: x > 3)
        result = collection.reverse()
        assert result.all() == [3, 1]

    def test_remove_modifies_original(self):
        """Test that remove modifies the original collection."""
        original_items = [1, 2, 2, 3, 4]
        collection = Collection(original_items)

        collection.remove(2)

        # Original collection should be modified
        assert collection.all() == [1, 3, 4]
