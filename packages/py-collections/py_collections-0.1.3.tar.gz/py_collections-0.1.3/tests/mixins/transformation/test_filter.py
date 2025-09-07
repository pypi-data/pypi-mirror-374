from py_collections.collection import Collection


class TestCollectionFilter:
    """Test suite for the Collection filter method."""

    def test_filter_basic_functionality(self):
        """Test basic filtering functionality."""
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Filter even numbers
        even_numbers = collection.filter(lambda x: x % 2 == 0)
        assert even_numbers.all() == [2, 4, 6, 8, 10]
        assert len(even_numbers) == 5

        # Filter odd numbers
        odd_numbers = collection.filter(lambda x: x % 2 == 1)
        assert odd_numbers.all() == [1, 3, 5, 7, 9]
        assert len(odd_numbers) == 5

    def test_filter_with_strings(self):
        """Test filtering with string collections."""
        collection = Collection(["apple", "banana", "cherry", "date", "elderberry"])

        # Filter strings starting with 'a'
        a_words = collection.filter(lambda s: s.startswith("a"))
        assert a_words.all() == ["apple"]
        assert len(a_words) == 1

        # Filter strings with length > 5
        long_words = collection.filter(lambda s: len(s) > 5)
        assert long_words.all() == ["banana", "cherry", "elderberry"]
        assert len(long_words) == 3

        # Filter strings containing 'e'
        e_words = collection.filter(lambda s: "e" in s)
        assert e_words.all() == ["apple", "cherry", "date", "elderberry"]
        assert len(e_words) == 4

    def test_filter_empty_collection(self):
        """Test filtering on empty collection."""
        collection = Collection()

        # Filter empty collection
        filtered = collection.filter(lambda x: x > 0)
        assert filtered.all() == []
        assert len(filtered) == 0
        assert isinstance(filtered, Collection)

    def test_filter_no_matches(self):
        """Test filtering when no elements match the predicate."""
        collection = Collection([1, 2, 3, 4, 5])

        # Filter for numbers > 100
        filtered = collection.filter(lambda x: x > 100)
        assert filtered.all() == []
        assert len(filtered) == 0
        assert isinstance(filtered, Collection)

        # Filter for negative numbers
        filtered = collection.filter(lambda x: x < 0)
        assert filtered.all() == []
        assert len(filtered) == 0

    def test_filter_all_matches(self):
        """Test filtering when all elements match the predicate."""
        collection = Collection([1, 2, 3, 4, 5])

        # Filter for numbers > 0
        filtered = collection.filter(lambda x: x > 0)
        assert filtered.all() == [1, 2, 3, 4, 5]
        assert len(filtered) == 5

    def test_filter_with_complex_objects(self):
        """Test filtering with complex objects."""

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
                Person("Eve", 22),
            ]
        )

        # Filter people over 30
        over_30 = people.filter(lambda p: p.age > 30)
        assert len(over_30) == 2
        assert over_30.all()[0].name == "Charlie"
        assert over_30.all()[1].name == "David"

        # Filter people with names starting with 'A'
        a_names = people.filter(lambda p: p.name.startswith("A"))
        assert len(a_names) == 1
        assert a_names.all()[0].name == "Alice"

    def test_filter_with_mixed_types(self):
        """Test filtering with mixed type collections."""
        mixed = Collection([1, "hello", 3.14, True, [1, 2, 3], None])

        # Filter integers (excluding booleans)
        integers = mixed.filter(
            lambda x: isinstance(x, int) and not isinstance(x, bool)
        )
        assert integers.all() == [1]
        assert len(integers) == 1

        # Filter strings
        strings = mixed.filter(lambda x: isinstance(x, str))
        assert strings.all() == ["hello"]
        assert len(strings) == 1

        # Filter booleans
        booleans = mixed.filter(lambda x: isinstance(x, bool))
        assert booleans.all() == [True]
        assert len(booleans) == 1

        # Filter truthy values
        truthy = mixed.filter(lambda x: bool(x))
        assert truthy.all() == [1, "hello", 3.14, True, [1, 2, 3]]
        assert len(truthy) == 5

    def test_filter_with_none_values(self):
        """Test filtering with None values."""
        collection = Collection([None, "hello", None, 42, None])

        # Filter None values
        none_values = collection.filter(lambda x: x is None)
        assert none_values.all() == [None, None, None]
        assert len(none_values) == 3

        # Filter non-None values
        non_none = collection.filter(lambda x: x is not None)
        assert non_none.all() == ["hello", 42]
        assert len(non_none) == 2

    def test_filter_returns_new_collection(self):
        """Test that filter returns a new collection instance."""
        original = Collection([1, 2, 3, 4, 5])
        filtered = original.filter(lambda x: x % 2 == 0)

        # Verify they are different instances
        assert filtered is not original
        assert filtered._items is not original._items

        # Verify original is unchanged
        assert original.all() == [1, 2, 3, 4, 5]
        assert len(original) == 5

    def test_filter_chaining(self):
        """Test chaining multiple filter operations."""
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Chain multiple filters
        result = collection.filter(lambda x: x % 2 == 0)  # Even numbers
        result = result.filter(lambda x: x > 5)  # Even numbers > 5
        result = result.filter(lambda x: x < 10)  # Even numbers 5 < x < 10

        assert result.all() == [6, 8]
        assert len(result) == 2

    def test_filter_with_duplicate_elements(self):
        """Test filtering with duplicate elements."""
        collection = Collection([1, 2, 2, 3, 2, 4, 5, 2])

        # Filter for number 2
        twos = collection.filter(lambda x: x == 2)
        assert twos.all() == [2, 2, 2, 2]
        assert len(twos) == 4

        # Filter for numbers > 2
        greater_than_2 = collection.filter(lambda x: x > 2)
        assert greater_than_2.all() == [3, 4, 5]
        assert len(greater_than_2) == 3

    def test_filter_with_empty_objects(self):
        """Test filtering with empty objects."""
        collection = Collection([[], {}, "", 0, None, False])

        # Filter empty lists
        empty_lists = collection.filter(lambda x: isinstance(x, list) and len(x) == 0)
        assert empty_lists.all() == [[]]
        assert len(empty_lists) == 1

        # Filter falsy values
        falsy = collection.filter(lambda x: not bool(x))
        assert falsy.all() == [[], {}, "", 0, None, False]
        assert len(falsy) == 6

    def test_filter_consistency_with_first(self):
        """Test that filter is consistent with first method."""
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Get first even number
        first_even = collection.first(lambda x: x % 2 == 0)

        # Filter all even numbers
        all_even = collection.filter(lambda x: x % 2 == 0)

        # First even should be the first element in filtered collection
        assert first_even == all_even.first()
        assert first_even == all_even.all()[0]
