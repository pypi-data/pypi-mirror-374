from py_collections.collection import Collection


class TestCollectionFirst:
    """Test suite for the Collection first method."""

    def test_first_element(self):
        """Test getting the first element from a collection."""
        collection = Collection([1, 2, 3, 4, 5])
        assert collection.first() == 1

        # Test with different data types
        mixed_collection = Collection(["hello", 42, {"key": "value"}])
        assert mixed_collection.first() == "hello"

        # Test with single element
        single_collection = Collection([999])
        assert single_collection.first() == 999

    def test_first_element_empty_collection(self):
        """Test that first() returns None on empty collection."""
        collection = Collection()

        assert collection.first() is None

    def test_first_element_after_append(self):
        """Test that first() returns the correct element after appending."""
        collection = Collection([10, 20, 30])
        assert collection.first() == 10

        collection.append(40)
        assert collection.first() == 10  # First element should remain the same

        # Create new collection and test first element
        new_collection = Collection()
        new_collection.append(100)
        assert new_collection.first() == 100

    def test_first_element_with_complex_objects(self):
        """Test first() with complex objects."""
        complex_items = [
            {"name": "John", "age": 30},
            [1, 2, 3],
            {"nested": {"key": "value"}},
        ]

        collection = Collection(complex_items)
        first_item = collection.first()
        assert first_item == {"name": "John", "age": 30}

    def test_first_element_with_none_values(self):
        """Test first() with None values in collection."""
        collection = Collection([None, "hello", 42])
        assert collection.first() is None

        # Test with None as first element after append
        empty_collection = Collection()
        empty_collection.append(None)
        assert empty_collection.first() is None

    def test_first_with_predicate(self):
        """Test first() with predicate function."""
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Test finding first even number
        assert collection.first(lambda x: x % 2 == 0) == 2

        # Test finding first number greater than 5
        assert collection.first(lambda x: x > 5) == 6

        # Test finding first number divisible by 3
        assert collection.first(lambda x: x % 3 == 0) == 3

        # Test with string collection
        str_collection = Collection(["apple", "banana", "cherry", "date"])
        assert str_collection.first(lambda s: s.startswith("b")) == "banana"
        assert str_collection.first(lambda s: len(s) > 5) == "banana"

    def test_first_with_predicate_no_match(self):
        """Test first() with predicate when no element matches."""
        collection = Collection([1, 2, 3, 4, 5])

        assert collection.first(lambda x: x > 100) is None

        str_collection = Collection(["apple", "banana"])
        assert str_collection.first(lambda s: s.startswith("z")) is None

    def test_first_with_predicate_empty_collection(self):
        """Test first() with predicate on empty collection."""
        collection = Collection()

        assert collection.first(lambda x: x > 0) is None

    def test_first_with_predicate_complex_objects(self):
        """Test first() with predicate on complex objects."""

        class Person:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

        people = Collection(
            [Person("Alice", 25), Person("Bob", 30), Person("Charlie", 35)]
        )

        # Test finding first person over 25
        first_over_25 = people.first(lambda p: p.age > 25)
        assert first_over_25.name == "Bob"
        assert first_over_25.age == 30

        # Test finding first person with name starting with 'C'
        first_c_name = people.first(lambda p: p.name.startswith("C"))
        assert first_c_name.name == "Charlie"
        assert first_c_name.age == 35

    def test_first_with_predicate_mixed_types(self):
        """Test first() with predicate on mixed type collection."""
        mixed = Collection([1, "hello", 3.14, True, [1, 2, 3]])

        # Test finding first string
        assert mixed.first(lambda x: isinstance(x, str)) == "hello"

        # Test finding first number (int or float)
        assert mixed.first(lambda x: isinstance(x, int | float)) == 1

        # Test finding first list
        assert mixed.first(lambda x: isinstance(x, list)) == [1, 2, 3]
