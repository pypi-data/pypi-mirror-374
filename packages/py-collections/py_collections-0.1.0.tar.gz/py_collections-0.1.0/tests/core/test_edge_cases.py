from py_collections.collection import Collection


class TestCollectionEdgeCases:
    """Test suite for Collection edge cases and integration scenarios."""

    def test_collection_independence(self):
        """Test that different Collection instances are independent."""
        collection1 = Collection([1, 2, 3])
        collection2 = Collection([4, 5, 6])

        collection1.append(7)
        collection2.append(8)

        assert collection1.all() == [1, 2, 3, 7]
        assert collection2.all() == [4, 5, 6, 8]

    def test_mutating_original_list(self):
        """Test that mutating the original list doesn't affect the collection."""
        original_list = [1, 2, 3]
        collection = Collection(original_list)

        # Mutate the original list
        original_list.append(4)

        # Collection should remain unchanged
        assert collection.all() == [1, 2, 3]
        assert len(collection) == 3

    def test_collection_with_complex_objects(self):
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

        collection.append({"new": "item"})
        assert len(collection) == 5

    def test_multiple_operations_chain(self):
        """Test chaining multiple operations on a collection."""
        collection = Collection([1, 2])

        # Chain multiple operations
        collection.append(3)
        first = collection.first()
        items = collection.all()
        length = len(collection)

        assert first == 1
        assert items == [1, 2, 3]
        assert length == 3
        assert str(collection) == "Collection([1, 2, 3])"

    def test_empty_collection_operations(self):
        """Test operations on empty collections."""
        collection = Collection()

        # Test all methods on empty collection
        assert len(collection) == 0
        assert collection.all() == []
        assert str(collection) == "Collection([])"
        assert repr(collection) == "Collection([])"

        # Test first() should return None for empty collection
        assert collection.first() is None

        # Test append to empty collection
        collection.append("first")
        assert len(collection) == 1
        assert collection.first() == "first"

    def test_collection_with_none_values(self):
        """Test collection behavior with None values."""
        collection = Collection([None, "hello", None, 42])

        assert len(collection) == 4
        assert collection.first() is None
        assert collection.all() == [None, "hello", None, 42]

        collection.append(None)
        assert len(collection) == 5

    def test_collection_with_empty_objects(self):
        """Test collection with empty objects."""
        collection = Collection([[], {}, "", 0])

        assert len(collection) == 4
        assert collection.first() == []
        assert collection.all() == [[], {}, "", 0]

        collection.append([])
        assert len(collection) == 5
