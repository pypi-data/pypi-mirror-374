import pytest

from py_collections.collection import Collection
from py_collections.mixins.element_access import ItemNotFoundException


class TestCollectionFirstOrRaise:
    """Test suite for the Collection first_or_raise method."""

    def test_first_or_raise_element_found(self):
        """Test getting the first element when it exists."""
        collection = Collection([1, 2, 3, 4, 5])

        # Test without predicate
        assert collection.first_or_raise() == 1

        # Test with different data types
        mixed_collection = Collection(["hello", 42, {"key": "value"}])
        assert mixed_collection.first_or_raise() == "hello"

        # Test with single element
        single_collection = Collection([999])
        assert single_collection.first_or_raise() == 999

    def test_first_or_raise_with_predicate_found(self):
        """Test first_or_raise with predicate when element is found."""
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Test finding first even number
        assert collection.first_or_raise(lambda x: x % 2 == 0) == 2

        # Test finding first number greater than 5
        assert collection.first_or_raise(lambda x: x > 5) == 6

        # Test finding first number divisible by 3
        assert collection.first_or_raise(lambda x: x % 3 == 0) == 3

        # Test with string collection
        str_collection = Collection(["apple", "banana", "cherry", "date"])
        assert str_collection.first_or_raise(lambda s: s.startswith("b")) == "banana"
        assert str_collection.first_or_raise(lambda s: len(s) > 5) == "banana"

    def test_first_or_raise_empty_collection(self):
        """Test that first_or_raise raises ItemNotFoundException on empty collection."""
        collection = Collection()

        with pytest.raises(
            ItemNotFoundException,
            match="Cannot get first element from empty collection",
        ):
            collection.first_or_raise()

        with pytest.raises(
            ItemNotFoundException,
            match="Cannot get first element from empty collection",
        ):
            collection.first_or_raise(lambda x: x > 0)

    def test_first_or_raise_no_match(self):
        """Test that first_or_raise raises ItemNotFoundException when no element matches."""
        collection = Collection([1, 2, 3, 4, 5])

        with pytest.raises(
            ItemNotFoundException, match="No element satisfies the predicate"
        ):
            collection.first_or_raise(lambda x: x > 100)

        str_collection = Collection(["apple", "banana"])
        with pytest.raises(
            ItemNotFoundException, match="No element satisfies the predicate"
        ):
            str_collection.first_or_raise(lambda s: s.startswith("z"))

    def test_first_or_raise_with_complex_objects(self):
        """Test first_or_raise with complex objects."""

        class Person:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

        people = Collection(
            [Person("Alice", 25), Person("Bob", 30), Person("Charlie", 35)]
        )

        # Test finding first person over 25
        first_over_25 = people.first_or_raise(lambda p: p.age > 25)
        assert first_over_25.name == "Bob"
        assert first_over_25.age == 30

        # Test finding first person with name starting with 'C'
        first_c_name = people.first_or_raise(lambda p: p.name.startswith("C"))
        assert first_c_name.name == "Charlie"
        assert first_c_name.age == 35

    def test_first_or_raise_with_mixed_types(self):
        """Test first_or_raise with mixed type collection."""
        mixed = Collection([1, "hello", 3.14, True, [1, 2, 3]])

        # Test finding first string
        assert mixed.first_or_raise(lambda x: isinstance(x, str)) == "hello"

        # Test finding first number (int or float)
        assert mixed.first_or_raise(lambda x: isinstance(x, int | float)) == 1

        # Test finding first list
        assert mixed.first_or_raise(lambda x: isinstance(x, list)) == [1, 2, 3]

    def test_first_or_raise_with_none_values(self):
        """Test first_or_raise with None values in collection."""
        collection = Collection([None, "hello", None, 42, None])

        # Test finding first None
        assert collection.first_or_raise(lambda x: x is None) is None

        # Test finding first non-None
        assert collection.first_or_raise(lambda x: x is not None) == "hello"

    def test_first_or_raise_consistency_with_first(self):
        """Test that first_or_raise is consistent with first method when element exists."""
        collection = Collection([1, 2, 3, 4, 5])

        # Test without predicate
        assert collection.first_or_raise() == collection.first()

        # Test with predicate
        assert collection.first_or_raise(lambda x: x % 2 == 0) == collection.first(
            lambda x: x % 2 == 0
        )
        assert collection.first_or_raise(lambda x: x > 3) == collection.first(
            lambda x: x > 3
        )

    def test_first_or_raise_exception_type(self):
        """Test that the correct exception type is raised."""
        collection = Collection([1, 2, 3])

        # Test empty collection
        empty = Collection()
        with pytest.raises(ItemNotFoundException):
            empty.first_or_raise()

        # Test no match
        with pytest.raises(ItemNotFoundException):
            collection.first_or_raise(lambda x: x > 100)

        # Verify it's not IndexError
        with pytest.raises(ItemNotFoundException):
            empty.first_or_raise()

        # Verify it's not ValueError
        with pytest.raises(ItemNotFoundException):
            collection.first_or_raise(lambda x: x > 100)

    def test_first_or_raise_exception_messages(self):
        """Test that the exception messages are descriptive."""
        collection = Collection([1, 2, 3])

        # Test empty collection message
        empty = Collection()
        try:
            empty.first_or_raise()
        except ItemNotFoundException as e:
            assert "Cannot get first element from empty collection" in str(e)

        # Test no match message
        try:
            collection.first_or_raise(lambda x: x > 100)
        except ItemNotFoundException as e:
            assert "No element satisfies the predicate" in str(e)

    def test_first_or_raise_after_append(self):
        """Test first_or_raise behavior after appending elements."""
        collection = Collection([10, 20, 30])
        assert collection.first_or_raise() == 10

        collection.append(40)
        assert collection.first_or_raise() == 10  # First element should remain the same

        # Create new collection and test first_or_raise
        new_collection = Collection()
        new_collection.append(100)
        assert new_collection.first_or_raise() == 100

    def test_first_or_raise_with_duplicate_elements(self):
        """Test first_or_raise with duplicate elements."""
        collection = Collection([1, 2, 2, 3, 2, 4])

        # Should return first occurrence of 2
        assert collection.first_or_raise(lambda x: x == 2) == 2

        # Should return first occurrence of 3
        assert collection.first_or_raise(lambda x: x == 3) == 3
