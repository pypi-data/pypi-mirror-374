from py_collections.collection import Collection


class TestCollectionLen:
    """Test suite for the Collection __len__ method."""

    def test_len_method(self):
        """Test the __len__ method."""
        collection = Collection([1, 2, 3, 4, 5])
        assert len(collection) == 5

        collection.append(6)
        assert len(collection) == 6

        empty_collection = Collection()
        assert len(empty_collection) == 0

    def test_len_empty_collection(self):
        """Test len on empty collection."""
        collection = Collection()
        assert len(collection) == 0

        collection = Collection([])
        assert len(collection) == 0

        collection = Collection(None)
        assert len(collection) == 0

    def test_len_after_append(self):
        """Test len after appending items."""
        collection = Collection([1, 2])
        assert len(collection) == 2

        collection.append(3)
        assert len(collection) == 3

        collection.append(4)
        collection.append(5)
        assert len(collection) == 5

    def test_len_with_complex_objects(self):
        """Test len with complex objects."""
        complex_items = [
            {"name": "John", "age": 30},
            [1, 2, 3],
            {"nested": {"key": "value"}},
            [],
        ]

        collection = Collection(complex_items)
        assert len(collection) == 4

        collection.append({"new": "item"})
        assert len(collection) == 5

    def test_len_multiple_collections(self):
        """Test len on multiple independent collections."""
        collection1 = Collection([1, 2, 3])
        collection2 = Collection([4, 5])
        collection3 = Collection()

        assert len(collection1) == 3
        assert len(collection2) == 2
        assert len(collection3) == 0

        collection1.append(4)
        collection2.append(6)
        collection3.append(1)

        assert len(collection1) == 4
        assert len(collection2) == 3
        assert len(collection3) == 1
