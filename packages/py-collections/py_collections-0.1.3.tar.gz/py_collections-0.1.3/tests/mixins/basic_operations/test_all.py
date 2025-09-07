from py_collections.collection import Collection


class TestCollectionAll:
    """Test suite for the Collection all method."""

    def test_all_items(self):
        """Test getting all items from a collection."""
        collection = Collection([1, 2, 3, 4, 5])
        all_items = collection.all()
        assert all_items == [1, 2, 3, 4, 5]
        assert isinstance(all_items, list)

    def test_all_empty_collection(self):
        """Test all() on empty collection."""
        collection = Collection()
        all_items = collection.all()
        assert all_items == []
        assert isinstance(all_items, list)

    def test_all_after_append(self):
        """Test all() after appending items."""
        collection = Collection([1, 2, 3])
        collection.append(4)
        collection.append(5)

        all_items = collection.all()
        assert all_items == [1, 2, 3, 4, 5]

    def test_all_returns_copy(self):
        """Test that all() returns a copy, not the original list."""
        original_items = [1, 2, 3]
        collection = Collection(original_items)
        returned_items = collection.all()

        # Modifying the returned list should not affect the collection
        returned_items.append(4)
        assert collection.all() == [1, 2, 3]
        assert returned_items == [1, 2, 3, 4]

    def test_all_with_different_types(self):
        """Test all() with different data types."""
        collection = Collection([42, "hello", [1, 2, 3], {"key": "value"}, None])
        all_items = collection.all()

        expected = [42, "hello", [1, 2, 3], {"key": "value"}, None]
        assert all_items == expected
        assert len(all_items) == 5

    def test_all_with_complex_objects(self):
        """Test all() with complex objects."""
        complex_items = [
            {"name": "John", "age": 30},
            [1, 2, 3],
            {"nested": {"key": "value"}},
            [],
        ]

        collection = Collection(complex_items)
        all_items = collection.all()

        assert all_items == complex_items
        assert len(all_items) == 4
        assert isinstance(all_items[0], dict)
        assert isinstance(all_items[1], list)

    def test_all_consistency(self):
        """Test that all() returns consistent results."""
        collection = Collection([1, 2, 3])

        # Multiple calls should return the same result
        all1 = collection.all()
        all2 = collection.all()
        assert all1 == all2 == [1, 2, 3]

        # After append, all should include new items
        collection.append(4)
        all3 = collection.all()
        assert all3 == [1, 2, 3, 4]

    def test_all_with_none_values(self):
        """Test all() with None values in collection."""
        collection = Collection([None, "hello", None, 42])
        all_items = collection.all()

        assert all_items == [None, "hello", None, 42]
        assert len(all_items) == 4
