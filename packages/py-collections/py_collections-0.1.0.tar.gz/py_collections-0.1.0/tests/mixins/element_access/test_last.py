import pytest

from py_collections.collection import Collection


class TestCollectionLast:
    """Test suite for the Collection last method."""

    def test_last_element(self):
        """Test getting the last element from a collection."""
        collection = Collection([1, 2, 3, 4, 5])
        assert collection.last() == 5

        # Test with different data types
        mixed_collection = Collection(["hello", 42, {"key": "value"}])
        assert mixed_collection.last() == {"key": "value"}

        # Test with single element
        single_collection = Collection([999])
        assert single_collection.last() == 999

    def test_last_element_empty_collection(self):
        """Test that last() raises IndexError on empty collection."""
        collection = Collection()

        with pytest.raises(
            IndexError, match="Cannot get last element from empty collection"
        ):
            collection.last()

    def test_last_element_after_append(self):
        """Test that last() returns the correct element after appending."""
        collection = Collection([10, 20, 30])
        assert collection.last() == 30

        collection.append(40)
        assert collection.last() == 40  # Last element should be the newly appended one

        # Create new collection and test last element
        new_collection = Collection()
        new_collection.append(100)
        assert new_collection.last() == 100

    def test_last_element_with_complex_objects(self):
        """Test last() with complex objects."""
        complex_items = [
            {"name": "John", "age": 30},
            [1, 2, 3],
            {"nested": {"key": "value"}},
        ]

        collection = Collection(complex_items)
        last_item = collection.last()
        assert last_item == {"nested": {"key": "value"}}

    def test_last_element_with_none_values(self):
        """Test last() with None values in collection."""
        collection = Collection([None, "hello", None, 42])
        assert collection.last() == 42

        # Test with None as last element after append
        empty_collection = Collection()
        empty_collection.append(None)
        assert empty_collection.last() is None

    def test_last_element_consistency(self):
        """Test that last() returns consistent results."""
        collection = Collection([1, 2, 3, 4, 5])

        # Multiple calls should return the same result
        last1 = collection.last()
        last2 = collection.last()
        assert last1 == last2 == 5

        # After append, last should change
        collection.append(6)
        assert collection.last() == 6

    def test_last_vs_first_comparison(self):
        """Test comparison between last() and first() methods."""
        collection = Collection([1, 2, 3, 4, 5])

        assert collection.first() == 1
        assert collection.last() == 5
        assert collection.first() != collection.last()

        # With single element, first and last should be the same
        single_collection = Collection([42])
        assert single_collection.first() == single_collection.last() == 42
