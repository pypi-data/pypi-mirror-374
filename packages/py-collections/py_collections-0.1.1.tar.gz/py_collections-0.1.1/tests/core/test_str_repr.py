from py_collections.collection import Collection


class TestCollectionStrRepr:
    """Test suite for the Collection __str__ and __repr__ methods."""

    def test_str_representation(self):
        """Test the __str__ method."""
        collection = Collection([1, 2, 3])
        assert str(collection) == "Collection([1, 2, 3])"

        empty_collection = Collection()
        assert str(empty_collection) == "Collection([])"

        collection_with_strings = Collection(["hello", "world"])
        assert str(collection_with_strings) == "Collection(['hello', 'world'])"

    def test_repr_representation(self):
        """Test the __repr__ method."""
        collection = Collection([1, 2, 3])
        assert repr(collection) == "Collection([1, 2, 3])"

        empty_collection = Collection()
        assert repr(empty_collection) == "Collection([])"

    def test_str_with_different_types(self):
        """Test str with different data types."""
        collection = Collection([42, "hello", None, [1, 2, 3]])
        expected = "Collection([42, 'hello', None, [1, 2, 3]])"
        assert str(collection) == expected

    def test_str_with_complex_objects(self):
        """Test str with complex nested objects."""
        complex_items = [
            {"name": "John", "age": 30},
            [1, 2, 3],
            {"nested": {"key": "value"}},
        ]

        collection = Collection(complex_items)
        str_repr = str(collection)

        # Should contain the basic structure
        assert "Collection(" in str_repr
        assert ")" in str_repr
        assert "John" in str_repr

    def test_str_after_append(self):
        """Test str representation after appending items."""
        collection = Collection([1, 2])
        assert str(collection) == "Collection([1, 2])"

        collection.append(3)
        assert str(collection) == "Collection([1, 2, 3])"

    def test_str_repr_consistency(self):
        """Test that str and repr return the same for simple cases."""
        collection = Collection([1, 2, 3])
        assert str(collection) == repr(collection)

        empty_collection = Collection()
        assert str(empty_collection) == repr(empty_collection)

    def test_str_with_empty_list(self):
        """Test str with empty list initialization."""
        collection = Collection([])
        assert str(collection) == "Collection([])"
        assert repr(collection) == "Collection([])"

    def test_str_with_none_initialization(self):
        """Test str with None initialization."""
        collection = Collection(None)
        assert str(collection) == "Collection([])"
        assert repr(collection) == "Collection([])"
