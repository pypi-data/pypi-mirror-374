from py_collections.collection import Collection


class TestCollectionAppend:
    """Test suite for the Collection append method."""

    def test_append_single_item(self):
        """Test appending a single item to an empty collection."""
        collection = Collection()
        collection.append(42)
        assert collection.all() == [42]
        assert len(collection) == 1

    def test_append_multiple_items(self):
        """Test appending multiple items to a collection."""
        collection = Collection([1, 2])
        collection.append(3)
        collection.append(4)
        collection.append(5)
        assert collection.all() == [1, 2, 3, 4, 5]
        assert len(collection) == 5

    def test_append_different_types(self):
        """Test appending items of different types."""
        collection = Collection()
        collection.append(42)
        collection.append("hello")
        collection.append([1, 2, 3])
        collection.append({"key": "value"})
        collection.append(None)

        expected = [42, "hello", [1, 2, 3], {"key": "value"}, None]
        assert collection.all() == expected
        assert len(collection) == 5

    def test_append_to_empty_collection(self):
        """Test appending to an empty collection."""
        collection = Collection()
        collection.append("first_item")
        assert collection.all() == ["first_item"]
        assert len(collection) == 1

    def test_append_after_initialization(self):
        """Test appending after initializing with items."""
        collection = Collection([10, 20, 30])
        collection.append(40)
        assert collection.all() == [10, 20, 30, 40]
        assert len(collection) == 4
