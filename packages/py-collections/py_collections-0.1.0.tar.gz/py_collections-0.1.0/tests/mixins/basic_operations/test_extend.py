import pytest

from py_collections.collection import Collection


class TestExtend:
    def test_extend_with_list(self):
        """Test extending a collection with a list."""
        collection = Collection([1, 2, 3])
        collection.extend([4, 5, 6])
        assert collection.all() == [1, 2, 3, 4, 5, 6]

    def test_extend_with_collection(self):
        """Test extending a collection with another collection."""
        collection = Collection([1, 2, 3])
        other_collection = Collection([4, 5, 6])
        collection.extend(other_collection)
        assert collection.all() == [1, 2, 3, 4, 5, 6]

    def test_extend_empty_collection(self):
        """Test extending an empty collection."""
        collection = Collection()
        other_collection = Collection([1, 2, 3])
        collection.extend(other_collection)
        assert collection.all() == [1, 2, 3]

    def test_extend_with_empty_list(self):
        """Test extending with an empty list."""
        collection = Collection([1, 2, 3])
        collection.extend([])
        assert collection.all() == [1, 2, 3]

    def test_extend_with_empty_collection(self):
        """Test extending with an empty collection."""
        collection = Collection([1, 2, 3])
        empty_collection = Collection()
        collection.extend(empty_collection)
        assert collection.all() == [1, 2, 3]

    def test_extend_multiple_times(self):
        """Test extending multiple times."""
        collection = Collection([1])
        collection.extend([2, 3])
        collection.extend(Collection([4, 5]))
        collection.extend([6])
        assert collection.all() == [1, 2, 3, 4, 5, 6]

    def test_extend_preserves_original_collection(self):
        """Test that extending doesn't modify the original collection passed as argument."""
        collection = Collection([1, 2, 3])
        other_collection = Collection([4, 5, 6])
        collection.extend(other_collection)

        # The original collection should remain unchanged
        assert other_collection.all() == [4, 5, 6]
        # The extended collection should have all items
        assert collection.all() == [1, 2, 3, 4, 5, 6]

    def test_extend_with_different_types(self):
        """Test extending with mixed types."""
        collection = Collection(["a", "b"])
        collection.extend([1, 2, 3])
        assert collection.all() == ["a", "b", 1, 2, 3]

    def test_extend_with_none_values(self):
        """Test extending with None values."""
        collection = Collection([1, 2])
        collection.extend([None, 3])
        assert collection.all() == [1, 2, None, 3]
