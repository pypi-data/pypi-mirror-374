import pytest

from py_collections import Collection


class TestTake:
    def test_take_positive_count(self):
        """Test taking a positive number of items from the beginning."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.take(2)
        assert result.all() == [1, 2]
        assert isinstance(result, Collection)

    def test_take_negative_count(self):
        """Test taking a negative number of items from the end."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.take(-2)
        assert result.all() == [4, 5]
        assert isinstance(result, Collection)

    def test_take_zero(self):
        """Test taking zero items."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.take(0)
        assert result.all() == []
        assert isinstance(result, Collection)

    def test_take_more_than_available(self):
        """Test taking more items than available."""
        collection = Collection([1, 2, 3])
        result = collection.take(5)
        assert result.all() == [1, 2, 3]
        assert isinstance(result, Collection)

    def test_take_negative_more_than_available(self):
        """Test taking negative count that exceeds available items."""
        collection = Collection([1, 2, 3])
        result = collection.take(-5)
        assert result.all() == [1, 2, 3]
        assert isinstance(result, Collection)

    def test_take_from_empty_collection(self):
        """Test taking from an empty collection."""
        collection = Collection()
        result = collection.take(3)
        assert result.all() == []
        assert isinstance(result, Collection)

    def test_take_negative_from_empty_collection(self):
        """Test taking negative count from an empty collection."""
        collection = Collection()
        result = collection.take(-3)
        assert result.all() == []
        assert isinstance(result, Collection)

    def test_take_all_items_positive(self):
        """Test taking all items with positive count."""
        collection = Collection([1, 2, 3])
        result = collection.take(3)
        assert result.all() == [1, 2, 3]
        assert isinstance(result, Collection)

    def test_take_all_items_negative(self):
        """Test taking all items with negative count."""
        collection = Collection([1, 2, 3])
        result = collection.take(-3)
        assert result.all() == [1, 2, 3]
        assert isinstance(result, Collection)

    def test_take_one_item_positive(self):
        """Test taking one item from the beginning."""
        collection = Collection([1, 2, 3])
        result = collection.take(1)
        assert result.all() == [1]
        assert isinstance(result, Collection)

    def test_take_one_item_negative(self):
        """Test taking one item from the end."""
        collection = Collection([1, 2, 3])
        result = collection.take(-1)
        assert result.all() == [3]
        assert isinstance(result, Collection)

    def test_take_original_collection_unchanged(self):
        """Test that the original collection remains unchanged."""
        collection = Collection([1, 2, 3, 4, 5])
        original_items = collection.all()
        result = collection.take(2)

        # Verify result is correct
        assert result.all() == [1, 2]

        # Verify original collection is unchanged
        assert collection.all() == original_items

    def test_take_with_strings(self):
        """Test take method with string items."""
        collection = Collection(["a", "b", "c", "d", "e"])
        result = collection.take(3)
        assert result.all() == ["a", "b", "c"]
        assert isinstance(result, Collection)

    def test_take_with_mixed_types(self):
        """Test take method with mixed type items."""
        collection = Collection([1, "two", 3.0, True, None])
        result = collection.take(-3)
        assert result.all() == [3.0, True, None]
        assert isinstance(result, Collection)

    def test_take_returns_new_collection(self):
        """Test that take returns a new collection instance."""
        collection = Collection([1, 2, 3])
        result = collection.take(2)
        assert result is not collection
        assert result._items is not collection._items
