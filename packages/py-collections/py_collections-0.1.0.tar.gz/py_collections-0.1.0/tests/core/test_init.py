from py_collections.collection import Collection


class TestCollectionInit:
    """Test suite for the Collection constructor."""

    def test_init_with_items(self):
        """Test initializing Collection with a list of items."""
        items = [1, 2, 3]
        collection = Collection(items)
        assert collection.all() == [1, 2, 3]
        assert len(collection) == 3

    def test_init_without_items(self):
        """Test initializing Collection without items (empty collection)."""
        collection = Collection()
        assert collection.all() == []
        assert len(collection) == 0

    def test_init_with_none(self):
        """Test initializing Collection with None (should create empty collection)."""
        collection = Collection(None)
        assert collection.all() == []
        assert len(collection) == 0

    def test_init_with_empty_list(self):
        """Test initializing Collection with an empty list."""
        collection = Collection([])
        assert collection.all() == []
        assert len(collection) == 0

    def test_init_with_complex_objects(self):
        """Test Collection with complex objects like dictionaries and lists."""
        complex_items = [
            {"name": "John", "age": 30},
            [1, 2, 3],
            {"nested": {"key": "value"}},
            [],
        ]

        collection = Collection(complex_items)
        assert len(collection) == 4
        assert collection.all() == complex_items
