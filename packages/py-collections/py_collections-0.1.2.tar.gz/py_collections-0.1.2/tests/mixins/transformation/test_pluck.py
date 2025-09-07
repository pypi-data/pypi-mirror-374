import pytest

from py_collections import Collection


class TestPluck:
    def test_pluck_basic_functionality(self):
        """Test basic pluck functionality with dictionary items."""
        users = Collection(
            [
                {"name": "Alice", "age": 25, "city": "New York"},
                {"name": "Bob", "age": 30, "city": "Los Angeles"},
                {"name": "Charlie", "age": 35, "city": "Chicago"},
            ]
        )
        result = users.pluck("name")
        assert result.all() == ["Alice", "Bob", "Charlie"]
        assert isinstance(result, Collection)

    def test_pluck_with_value_key(self):
        """Test pluck with both key and value_key parameters."""
        users = Collection(
            [
                {"name": "Alice", "age": 25, "city": "New York"},
                {"name": "Bob", "age": 30, "city": "Los Angeles"},
                {"name": "Charlie", "age": 35, "city": "Chicago"},
            ]
        )
        result = users.pluck("name", "age")
        expected = [{"Alice": 25}, {"Bob": 30}, {"Charlie": 35}]
        assert result.all() == expected
        assert isinstance(result, Collection)

    def test_pluck_with_objects(self):
        """Test pluck with object attributes."""

        class User:
            def __init__(self, name, age, city):
                self.name = name
                self.age = age
                self.city = city

        users = Collection(
            [
                User("Alice", 25, "New York"),
                User("Bob", 30, "Los Angeles"),
                User("Charlie", 35, "Chicago"),
            ]
        )
        result = users.pluck("name")
        assert result.all() == ["Alice", "Bob", "Charlie"]
        assert isinstance(result, Collection)

    def test_pluck_objects_with_value_key(self):
        """Test pluck with objects using both key and value_key."""

        class User:
            def __init__(self, name, age, city):
                self.name = name
                self.age = age
                self.city = city

        users = Collection(
            [
                User("Alice", 25, "New York"),
                User("Bob", 30, "Los Angeles"),
                User("Charlie", 35, "Chicago"),
            ]
        )
        result = users.pluck("name", "age")
        expected = [{"Alice": 25}, {"Bob": 30}, {"Charlie": 35}]
        assert result.all() == expected
        assert isinstance(result, Collection)

    def test_pluck_empty_collection(self):
        """Test pluck with empty collection."""
        collection = Collection()
        result = collection.pluck("name")
        assert result.all() == []
        assert isinstance(result, Collection)

    def test_pluck_missing_key(self):
        """Test pluck when key doesn't exist in items."""
        users = Collection([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
        result = users.pluck("city")
        assert result.all() == [None, None]
        assert isinstance(result, Collection)

    def test_pluck_missing_value_key(self):
        """Test pluck when value_key doesn't exist."""
        users = Collection([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
        result = users.pluck("name", "city")
        expected = [{"Alice": None}, {"Bob": None}]
        assert result.all() == expected
        assert isinstance(result, Collection)

    def test_pluck_mixed_types(self):
        """Test pluck with mixed dictionary and object items."""

        class User:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        users = Collection(
            [
                {"name": "Alice", "age": 25},
                User("Bob", 30),
                {"name": "Charlie", "age": 35},
            ]
        )
        result = users.pluck("name")
        assert result.all() == ["Alice", "Bob", "Charlie"]
        assert isinstance(result, Collection)

    def test_pluck_with_none_values(self):
        """Test pluck with None values in the data."""
        users = Collection(
            [
                {"name": "Alice", "age": 25, "city": None},
                {"name": None, "age": 30, "city": "Los Angeles"},
                {"name": "Charlie", "age": None, "city": "Chicago"},
            ]
        )
        result = users.pluck("name")
        assert result.all() == ["Alice", None, "Charlie"]
        assert isinstance(result, Collection)

    def test_pluck_with_none_values_and_value_key(self):
        """Test pluck with None values when using value_key."""
        users = Collection(
            [
                {"name": "Alice", "age": 25, "city": None},
                {"name": None, "age": 30, "city": "Los Angeles"},
                {"name": "Charlie", "age": None, "city": "Chicago"},
            ]
        )
        result = users.pluck("name", "age")
        expected = [{"Alice": 25}, {None: 30}, {"Charlie": None}]
        assert result.all() == expected
        assert isinstance(result, Collection)

    def test_pluck_with_complex_objects(self):
        """Test pluck with complex objects."""

        class Address:
            def __init__(self, street, city):
                self.street = street
                self.city = city

        class User:
            def __init__(self, name, address):
                self.name = name
                self.address = address

        users = Collection(
            [
                User("Alice", Address("123 Main St", "New York")),
                User("Bob", Address("456 Oak Ave", "Los Angeles")),
            ]
        )
        result = users.pluck("name")
        assert result.all() == ["Alice", "Bob"]
        assert isinstance(result, Collection)

    def test_pluck_original_collection_unchanged(self):
        """Test that the original collection remains unchanged."""
        users = Collection([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
        original_items = users.all()
        result = users.pluck("name")

        # Verify result is correct
        assert result.all() == ["Alice", "Bob"]

        # Verify original collection is unchanged
        assert users.all() == original_items

    def test_pluck_returns_new_collection(self):
        """Test that pluck returns a new collection instance."""
        users = Collection([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
        result = users.pluck("name")
        assert result is not users
        assert result._items is not users._items

    def test_pluck_with_different_data_types(self):
        """Test pluck with different data types as values."""
        data = Collection(
            [
                {"name": "Alice", "score": 95.5, "active": True},
                {"name": "Bob", "score": 87, "active": False},
                {"name": "Charlie", "score": 92.0, "active": True},
            ]
        )
        result = data.pluck("score")
        assert result.all() == [95.5, 87, 92.0]
        assert isinstance(result, Collection)

    def test_pluck_with_lists_as_values(self):
        """Test pluck with lists as values."""
        data = Collection(
            [
                {"name": "Alice", "hobbies": ["reading", "swimming"]},
                {"name": "Bob", "hobbies": ["gaming", "cooking"]},
            ]
        )
        result = data.pluck("hobbies")
        expected = [["reading", "swimming"], ["gaming", "cooking"]]
        assert result.all() == expected
        assert isinstance(result, Collection)

    def test_pluck_with_nested_dictionaries(self):
        """Test pluck with nested dictionary values."""
        data = Collection(
            [
                {"name": "Alice", "address": {"city": "New York", "country": "USA"}},
                {"name": "Bob", "address": {"city": "London", "country": "UK"}},
            ]
        )
        result = data.pluck("address")
        expected = [
            {"city": "New York", "country": "USA"},
            {"city": "London", "country": "UK"},
        ]
        assert result.all() == expected
        assert isinstance(result, Collection)

    def test_pluck_chaining(self):
        """Test chaining pluck operations."""
        users = Collection(
            [
                {"name": "Alice", "age": 25, "city": "New York"},
                {"name": "Bob", "age": 30, "city": "Los Angeles"},
            ]
        )
        result = users.pluck("name").map(str.upper)
        assert result.all() == ["ALICE", "BOB"]
        assert isinstance(result, Collection)

    def test_pluck_with_filter(self):
        """Test pluck combined with filter."""
        users = Collection(
            [
                {"name": "Alice", "age": 25, "active": True},
                {"name": "Bob", "age": 30, "active": False},
                {"name": "Charlie", "age": 35, "active": True},
            ]
        )
        result = users.filter(lambda x: x["active"]).pluck("name")
        assert result.all() == ["Alice", "Charlie"]
        assert isinstance(result, Collection)

    def test_pluck_with_empty_string_key(self):
        """Test pluck with empty string as key."""
        data = Collection(
            [
                {"": "empty_key_value", "name": "Alice"},
                {"": "another_empty", "name": "Bob"},
            ]
        )
        result = data.pluck("")
        assert result.all() == ["empty_key_value", "another_empty"]
        assert isinstance(result, Collection)

    def test_pluck_with_special_characters_in_key(self):
        """Test pluck with special characters in key names."""
        data = Collection(
            [
                {"user-name": "Alice", "user_age": 25},
                {"user-name": "Bob", "user_age": 30},
            ]
        )
        result = data.pluck("user-name")
        assert result.all() == ["Alice", "Bob"]
        assert isinstance(result, Collection)

    def test_pluck_with_nested_keys(self):
        """Test pluck with nested dictionary keys using dot notation."""
        users = Collection(
            [
                {"name": "Alice", "address": {"city": "New York", "country": "USA"}},
                {"name": "Bob", "address": {"city": "Los Angeles", "country": "USA"}},
                {"name": "Charlie", "address": {"city": "Chicago", "country": "USA"}},
            ]
        )
        result = users.pluck("address.city")
        assert result.all() == ["New York", "Los Angeles", "Chicago"]
        assert isinstance(result, Collection)

    def test_pluck_with_deeply_nested_keys(self):
        """Test pluck with deeply nested dictionary keys."""
        data = Collection(
            [
                {"user": {"profile": {"contact": {"email": "alice@example.com"}}}},
                {"user": {"profile": {"contact": {"email": "bob@example.com"}}}},
            ]
        )
        result = data.pluck("user.profile.contact.email")
        assert result.all() == ["alice@example.com", "bob@example.com"]
        assert isinstance(result, Collection)

    def test_pluck_with_nested_keys_and_value_key(self):
        """Test pluck with nested keys and value_key parameter."""
        users = Collection(
            [
                {"name": "Alice", "address": {"city": "New York", "zip": "10001"}},
                {"name": "Bob", "address": {"city": "Los Angeles", "zip": "90210"}},
            ]
        )
        result = users.pluck("name", "address.city")
        expected = [{"Alice": "New York"}, {"Bob": "Los Angeles"}]
        assert result.all() == expected
        assert isinstance(result, Collection)

    def test_pluck_with_nested_keys_both_parameters(self):
        """Test pluck with both key and value_key being nested."""
        users = Collection(
            [
                {"name": "Alice", "address": {"city": "New York", "country": "USA"}},
                {"name": "Bob", "address": {"city": "Los Angeles", "country": "USA"}},
            ]
        )
        result = users.pluck("address.city", "address.country")
        expected = [{"New York": "USA"}, {"Los Angeles": "USA"}]
        assert result.all() == expected
        assert isinstance(result, Collection)

    def test_pluck_with_nested_keys_missing_intermediate(self):
        """Test pluck with nested keys where intermediate keys don't exist."""
        users = Collection(
            [
                {"name": "Alice", "address": {"city": "New York"}},
                {"name": "Bob"},  # No address
                {"name": "Charlie", "address": {"city": "Chicago"}},
            ]
        )
        result = users.pluck("address.city")
        assert result.all() == ["New York", None, "Chicago"]
        assert isinstance(result, Collection)

    def test_pluck_with_nested_keys_missing_final(self):
        """Test pluck with nested keys where final key doesn't exist."""
        users = Collection(
            [
                {"name": "Alice", "address": {"city": "New York"}},
                {"name": "Bob", "address": {}},  # No city
                {"name": "Charlie", "address": {"city": "Chicago"}},
            ]
        )
        result = users.pluck("address.city")
        assert result.all() == ["New York", None, "Chicago"]
        assert isinstance(result, Collection)

    def test_pluck_with_nested_objects(self):
        """Test pluck with nested object attributes."""

        class Address:
            def __init__(self, city, country):
                self.city = city
                self.country = country

        class User:
            def __init__(self, name, address):
                self.name = name
                self.address = address

        users = Collection(
            [
                User("Alice", Address("New York", "USA")),
                User("Bob", Address("Los Angeles", "USA")),
            ]
        )
        result = users.pluck("address.city")
        assert result.all() == ["New York", "Los Angeles"]
        assert isinstance(result, Collection)

    def test_pluck_with_mixed_nested_types(self):
        """Test pluck with mixed nested dictionary and object types."""

        class Address:
            def __init__(self, city):
                self.city = city

        users = Collection(
            [
                {"name": "Alice", "address": {"city": "New York"}},
                {"name": "Bob", "address": Address("Los Angeles")},
            ]
        )
        result = users.pluck("address.city")
        assert result.all() == ["New York", "Los Angeles"]
        assert isinstance(result, Collection)

    def test_pluck_with_nested_none_values(self):
        """Test pluck with nested None values."""
        users = Collection(
            [
                {"name": "Alice", "address": {"city": "New York"}},
                {"name": "Bob", "address": None},
                {"name": "Charlie", "address": {"city": None}},
            ]
        )
        result = users.pluck("address.city")
        assert result.all() == ["New York", None, None]
        assert isinstance(result, Collection)

    def test_pluck_missing_attribute(self):
        """Test pluck when object doesn't have the requested attribute."""

        class User:
            def __init__(self, name, age):
                self.name = name
                self.age = age
                # Note: no 'city' attribute

        users = Collection(
            [
                User("Alice", 25),
                User("Bob", 30),
            ]
        )

        # This should return None for missing attributes
        result = users.pluck("city")
        assert result.all() == [None, None]
        assert isinstance(result, Collection)
