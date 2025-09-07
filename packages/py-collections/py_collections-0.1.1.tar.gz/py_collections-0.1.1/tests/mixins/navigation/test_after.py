from py_collections.collection import Collection


class TestCollectionAfter:
    """Test suite for the Collection after method."""

    def test_after_element_found(self):
        """Test getting the element after a specific element."""
        collection = Collection([1, 2, 3, 4, 5])

        # Test finding element after 2
        assert collection.after(2) == 3

        # Test finding element after 4
        assert collection.after(4) == 5

        # Test with string collection
        str_collection = Collection(["apple", "banana", "cherry", "date"])
        assert str_collection.after("banana") == "cherry"

    def test_after_element_not_found(self):
        """Test after() when target element is not found."""
        collection = Collection([1, 2, 3, 4, 5])

        # Element doesn't exist
        assert collection.after(10) is None

        # Test with string collection
        str_collection = Collection(["apple", "banana", "cherry"])
        assert str_collection.after("orange") is None

    def test_after_element_last(self):
        """Test after() when target element is the last element."""
        collection = Collection([1, 2, 3, 4, 5])

        # 5 is the last element, so there's no element after it
        assert collection.after(5) is None

        # Test with single element collection
        single_collection = Collection([42])
        assert single_collection.after(42) is None

    def test_after_empty_collection(self):
        """Test after() on empty collection."""
        collection = Collection()

        assert collection.after(1) is None
        assert collection.after(lambda x: x > 0) is None

    def test_after_with_predicate(self):
        """Test after() with predicate function."""
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Test finding element after first even number
        assert collection.after(lambda x: x % 2 == 0) == 3

        # Test finding element after first number greater than 5
        assert collection.after(lambda x: x > 5) == 7

        # Test finding element after first number divisible by 3
        assert collection.after(lambda x: x % 3 == 0) == 4

        # Test with string collection
        str_collection = Collection(["apple", "banana", "cherry", "date", "elderberry"])
        assert str_collection.after(lambda s: s.startswith("b")) == "cherry"
        assert str_collection.after(lambda s: len(s) > 5) == "cherry"

    def test_after_with_predicate_no_match(self):
        """Test after() with predicate when no element matches."""
        collection = Collection([1, 2, 3, 4, 5])

        assert collection.after(lambda x: x > 100) is None

        str_collection = Collection(["apple", "banana"])
        assert str_collection.after(lambda s: s.startswith("z")) is None

    def test_after_with_predicate_last_match(self):
        """Test after() with predicate when match is the last element."""
        collection = Collection([1, 2, 3, 4, 5])

        # 5 is the last element and matches the predicate
        assert collection.after(lambda x: x == 5) is None

        # Test with predicate that matches last element
        assert collection.after(lambda x: x > 4) is None

    def test_after_with_complex_objects(self):
        """Test after() with complex objects."""

        class Person:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

        people = Collection(
            [
                Person("Alice", 25),
                Person("Bob", 30),
                Person("Charlie", 35),
                Person("David", 40),
            ]
        )

        # Test finding element after person over 25
        result = people.after(lambda p: p.age > 25)
        assert result.name == "Charlie"
        assert result.age == 35

        # Test finding element after person with name starting with 'B'
        result = people.after(lambda p: p.name.startswith("B"))
        assert result.name == "Charlie"
        assert result.age == 35

    def test_after_with_mixed_types(self):
        """Test after() with mixed type collection."""
        mixed = Collection([1, "hello", 3.14, True, [1, 2, 3]])

        # Test finding element after first string
        assert mixed.after(lambda x: isinstance(x, str)) == 3.14

        # Test finding element after first number (int or float)
        assert mixed.after(lambda x: isinstance(x, int | float)) == "hello"

        # Test finding element after first list
        assert (
            mixed.after(lambda x: isinstance(x, list)) is None
        )  # List is last element

    def test_after_with_none_values(self):
        """Test after() with None values in collection."""
        collection = Collection([None, "hello", None, 42, None])

        # Test finding element after None
        assert collection.after(None) == "hello"

        # Test finding element after second None
        assert collection.after(lambda x: x is None) == "hello"

        # Test finding element after last None
        assert (
            collection.after(lambda x: x is None and collection.all().index(x) == 4)
            is None
        )

    def test_after_with_duplicate_elements(self):
        """Test after() with duplicate elements."""
        collection = Collection([1, 2, 2, 3, 2, 4])

        # Should return element after first occurrence of 2
        assert collection.after(2) == 2

        # Test with predicate that matches multiple elements
        assert collection.after(lambda x: x == 2) == 2

    def test_after_consistency_with_first(self):
        """Test that after() is consistent with first() behavior."""
        collection = Collection([1, 2, 3, 4, 5])

        # If we find the first even number and then get the element after it
        first_even = collection.first(lambda x: x % 2 == 0)  # 2
        after_first_even = collection.after(lambda x: x % 2 == 0)  # 3

        assert first_even == 2
        assert after_first_even == 3

        # Verify the relationship
        assert after_first_even == collection.after(first_even)
