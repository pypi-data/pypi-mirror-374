import pytest

from py_collections import Collection, CollectionMap


class TestCollectionMap:
    """Test cases for CollectionMap functionality."""

    def test_init_empty(self):
        """Test initializing an empty CollectionMap."""
        cmap = CollectionMap()
        assert len(cmap) == 0
        assert cmap._data == {}

    def test_init_with_dict(self):
        """Test initializing with a dictionary."""
        data = {"group1": Collection([1, 2, 3]), "group2": [4, 5, 6], "group3": 7}
        cmap = CollectionMap(data)

        assert len(cmap) == 3
        assert "group1" in cmap
        assert "group2" in cmap
        assert "group3" in cmap

        assert isinstance(cmap["group1"], Collection)
        assert isinstance(cmap["group2"], Collection)
        assert isinstance(cmap["group3"], Collection)

        assert cmap["group1"].all() == [1, 2, 3]
        assert cmap["group2"].all() == [4, 5, 6]
        assert cmap["group3"].all() == [7]

    def test_setitem_collection(self):
        """Test setting a Collection value."""
        cmap = CollectionMap()
        collection = Collection([1, 2, 3])
        cmap["test"] = collection

        assert "test" in cmap
        assert cmap["test"] is collection

    def test_setitem_list(self):
        """Test setting a list value."""
        cmap = CollectionMap()
        cmap["test"] = [1, 2, 3]

        assert "test" in cmap
        assert isinstance(cmap["test"], Collection)
        assert cmap["test"].all() == [1, 2, 3]

    def test_setitem_single_item(self):
        """Test setting a single item value."""
        cmap = CollectionMap()
        cmap["test"] = 42

        assert "test" in cmap
        assert isinstance(cmap["test"], Collection)
        assert cmap["test"].all() == [42]

    def test_getitem(self):
        """Test getting a value."""
        cmap = CollectionMap()
        cmap["test"] = Collection([1, 2, 3])

        result = cmap["test"]
        assert isinstance(result, Collection)
        assert result.all() == [1, 2, 3]

    def test_getitem_key_error(self):
        """Test KeyError when getting non-existent key."""
        cmap = CollectionMap()

        with pytest.raises(KeyError, match="Key 'missing' not found in CollectionMap"):
            cmap["missing"]

    def test_delitem(self):
        """Test deleting a key-value pair."""
        cmap = CollectionMap()
        cmap["test"] = Collection([1, 2, 3])

        assert "test" in cmap
        del cmap["test"]
        assert "test" not in cmap

    def test_contains(self):
        """Test checking if key exists."""
        cmap = CollectionMap()
        cmap["test"] = Collection([1, 2, 3])

        assert "test" in cmap
        assert "missing" not in cmap

    def test_len(self):
        """Test getting the length."""
        cmap = CollectionMap()
        assert len(cmap) == 0

        cmap["a"] = Collection([1])
        cmap["b"] = Collection([2])
        assert len(cmap) == 2

    def test_iter(self):
        """Test iterating over keys."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1])
        cmap["b"] = Collection([2])

        keys = list(cmap)
        assert "a" in keys
        assert "b" in keys
        assert len(keys) == 2

    def test_keys(self):
        """Test getting all keys."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1])
        cmap["b"] = Collection([2])

        keys = cmap.keys()
        assert "a" in keys
        assert "b" in keys
        assert len(keys) == 2

    def test_values(self):
        """Test getting all values."""
        cmap = CollectionMap()
        collection1 = Collection([1])
        collection2 = Collection([2])
        cmap["a"] = collection1
        cmap["b"] = collection2

        values = cmap.values()
        assert collection1 in values
        assert collection2 in values
        assert len(values) == 2
        assert all(isinstance(v, Collection) for v in values)

    def test_items(self):
        """Test getting all items."""
        cmap = CollectionMap()
        collection1 = Collection([1])
        collection2 = Collection([2])
        cmap["a"] = collection1
        cmap["b"] = collection2

        items = cmap.items()
        assert ("a", collection1) in items
        assert ("b", collection2) in items
        assert len(items) == 2

    def test_get(self):
        """Test getting with default value."""
        cmap = CollectionMap()
        cmap["test"] = Collection([1, 2, 3])

        # Existing key
        result = cmap.get("test")
        assert isinstance(result, Collection)
        assert result.all() == [1, 2, 3]

        # Non-existing key with default
        default = Collection([4, 5])
        result = cmap.get("missing", default)
        assert result is default

        # Non-existing key without default - should return empty collection
        result = cmap.get("missing")
        assert isinstance(result, Collection)
        assert len(result) == 0

    def test_setdefault(self):
        """Test setdefault functionality."""
        cmap = CollectionMap()

        # Key doesn't exist, should create empty collection
        result = cmap.setdefault("test")
        assert isinstance(result, Collection)
        assert len(result) == 0
        assert "test" in cmap

        # Key doesn't exist, should create with default
        result = cmap.setdefault("test2", [1, 2, 3])
        assert isinstance(result, Collection)
        assert result.all() == [1, 2, 3]
        assert "test2" in cmap

        # Key exists, should return existing value
        existing = cmap["test"]
        result = cmap.setdefault("test", [9, 8, 7])
        assert result is existing
        assert result.all() == []  # Should still be empty

    def test_update(self):
        """Test updating with another dictionary."""
        cmap = CollectionMap()
        cmap["existing"] = Collection([1])

        update_data = {"new1": Collection([2]), "new2": [3, 4], "new3": 5}
        cmap.update(update_data)

        assert len(cmap) == 4
        assert "existing" in cmap
        assert "new1" in cmap
        assert "new2" in cmap
        assert "new3" in cmap

        assert cmap["new1"].all() == [2]
        assert cmap["new2"].all() == [3, 4]
        assert cmap["new3"].all() == [5]

    def test_clear(self):
        """Test clearing all items."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1])
        cmap["b"] = Collection([2])

        assert len(cmap) == 2
        cmap.clear()
        assert len(cmap) == 0
        assert cmap._data == {}

    def test_pop(self):
        """Test popping a key-value pair."""
        cmap = CollectionMap()
        collection = Collection([1, 2, 3])
        cmap["test"] = collection

        # Pop existing key
        result = cmap.pop("test")
        assert result is collection
        assert "test" not in cmap

        # Pop non-existing key with default
        default = Collection([4, 5])
        result = cmap.pop("missing", default)
        assert result is default

        # Pop non-existing key without default
        result = cmap.pop("missing")
        assert result is None

    def test_popitem(self):
        """Test popping an arbitrary item."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1])
        cmap["b"] = Collection([2])

        key, collection = cmap.popitem()
        assert key in ["a", "b"]
        assert isinstance(collection, Collection)
        assert len(cmap) == 1

    def test_popitem_empty(self):
        """Test popitem on empty CollectionMap."""
        cmap = CollectionMap()

        with pytest.raises(KeyError, match="CollectionMap is empty"):
            cmap.popitem()

    def test_copy(self):
        """Test creating a shallow copy."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2, 3])
        cmap["b"] = Collection([4, 5, 6])

        copy = cmap.copy()
        assert len(copy) == 2
        assert "a" in copy
        assert "b" in copy
        assert copy["a"].all() == [1, 2, 3]
        assert copy["b"].all() == [4, 5, 6]

        # Should be shallow copy - Collection objects should be the same
        assert copy["a"] is cmap["a"]
        assert copy["b"] is cmap["b"]

        # But the CollectionMap itself should be different
        assert copy is not cmap

    def test_flatten(self):
        """Test flattening all collections."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2])
        cmap["b"] = Collection([3, 4, 5])
        cmap["c"] = Collection([6])

        result = cmap.flatten()
        assert isinstance(result, Collection)
        assert result.all() == [1, 2, 3, 4, 5, 6]

    def test_map(self):
        """Test mapping over collections."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2, 3])
        cmap["b"] = Collection([4, 5])
        cmap["c"] = Collection([6])

        result = cmap.map(len)
        assert result == {"a": 3, "b": 2, "c": 1}

        result = cmap.map(lambda c: c.first())
        assert result == {"a": 1, "b": 4, "c": 6}

    def test_filter(self):
        """Test filtering the CollectionMap."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2, 3])
        cmap["b"] = Collection([4, 5])
        cmap["c"] = Collection([6])

        # Filter by collection size
        result = cmap.filter(lambda key, collection: len(collection) > 2)
        assert len(result) == 1
        assert "a" in result

        # Filter by key
        result = cmap.filter(lambda key, collection: key.startswith("a"))
        assert len(result) == 1
        assert "a" in result

    def test_filter_by_size(self):
        """Test filtering by collection size."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2, 3])
        cmap["b"] = Collection([4, 5])
        cmap["c"] = Collection([6])

        # Filter by minimum size
        result = cmap.filter_by_size(min_size=2)
        assert len(result) == 2
        assert "a" in result
        assert "b" in result
        assert "c" not in result

        # Filter by size range
        result = cmap.filter_by_size(min_size=1, max_size=2)
        assert len(result) == 2
        assert "b" in result
        assert "c" in result
        assert "a" not in result

    def test_total_items(self):
        """Test getting total number of items."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2, 3])
        cmap["b"] = Collection([4, 5])
        cmap["c"] = Collection([6])

        total = cmap.total_items()
        assert total == 6

    def test_largest_group(self):
        """Test getting the largest group."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2, 3])
        cmap["b"] = Collection([4, 5])
        cmap["c"] = Collection([6])

        key, collection = cmap.largest_group()
        assert key == "a"
        assert collection.all() == [1, 2, 3]

    def test_largest_group_empty(self):
        """Test largest_group on empty CollectionMap."""
        cmap = CollectionMap()

        result = cmap.largest_group()
        assert result is None

    def test_smallest_group(self):
        """Test getting the smallest group."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2, 3])
        cmap["b"] = Collection([4, 5])
        cmap["c"] = Collection([6])

        key, collection = cmap.smallest_group()
        assert key == "c"
        assert collection.all() == [6]

    def test_smallest_group_empty(self):
        """Test smallest_group on empty CollectionMap."""
        cmap = CollectionMap()

        result = cmap.smallest_group()
        assert result is None

    def test_group_sizes(self):
        """Test getting group sizes."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2, 3])
        cmap["b"] = Collection([4, 5])
        cmap["c"] = Collection([6])

        sizes = cmap.group_sizes()
        assert sizes == {"a": 3, "b": 2, "c": 1}

    def test_add_new_key(self):
        """Test adding items to a new key."""
        cmap = CollectionMap()

        # Add Collection to new key
        cmap.add("test", Collection([1, 2, 3]))
        assert "test" in cmap
        assert cmap["test"].all() == [1, 2, 3]

        # Add list to new key
        cmap.add("list_key", [4, 5, 6])
        assert "list_key" in cmap
        assert cmap["list_key"].all() == [4, 5, 6]

        # Add single item to new key
        cmap.add("single", 42)
        assert "single" in cmap
        assert cmap["single"].all() == [42]

    def test_add_existing_key(self):
        """Test adding items to an existing key."""
        cmap = CollectionMap()
        cmap["test"] = Collection([1, 2, 3])

        # Add Collection to existing key
        cmap.add("test", Collection([4, 5]))
        assert cmap["test"].all() == [1, 2, 3, 4, 5]

        # Add list to existing key
        cmap.add("test", [6, 7])
        assert cmap["test"].all() == [1, 2, 3, 4, 5, 6, 7]

        # Add single item to existing key
        cmap.add("test", 8)
        assert cmap["test"].all() == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_add_mixed_types(self):
        """Test adding different types of items."""
        cmap = CollectionMap()

        # Start with empty collection
        cmap.add("mixed", [])
        assert cmap["mixed"].all() == []

        # Add different types
        cmap.add("mixed", Collection([1, 2]))
        cmap.add("mixed", ["hello", "world"])
        cmap.add("mixed", 42)
        cmap.add("mixed", [True, False])

        expected = [1, 2, "hello", "world", 42, True, False]
        assert cmap["mixed"].all() == expected

    def test_str_repr(self):
        """Test string representation."""
        cmap = CollectionMap()
        cmap["a"] = Collection([1, 2])
        cmap["b"] = Collection([3])

        result = str(cmap)
        assert "CollectionMap" in result
        assert "'a'" in result
        assert "'b'" in result
        assert "Collection([1, 2])" in result
        assert "Collection([3])" in result

        # Test __repr__ method
        repr_result = repr(cmap)
        assert repr_result == result  # __repr__ should return the same as __str__
