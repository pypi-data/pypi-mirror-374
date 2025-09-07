from py_collections.collection import Collection


class TestExists:
    def test_exists_with_empty_collection(self):
        """Test exists() returns False for empty collection."""
        collection = Collection()
        assert collection.exists() is False

    def test_exists_with_non_empty_collection(self):
        """Test exists() returns True for non-empty collection."""
        collection = Collection([1, 2, 3])
        assert collection.exists() is True

    def test_exists_with_predicate_matching_element(self):
        """Test exists() returns True when predicate matches an element."""
        collection = Collection([1, 2, 3, 4, 5])
        assert collection.exists(lambda x: x > 3) is True
        assert collection.exists(lambda x: x == 3) is True

    def test_exists_with_predicate_not_matching(self):
        """Test exists() returns False when predicate doesn't match any element."""
        collection = Collection([1, 2, 3, 4, 5])
        assert collection.exists(lambda x: x > 10) is False
        assert collection.exists(lambda x: x < 0) is False

    def test_exists_with_string_elements(self):
        """Test exists() with string elements."""
        collection = Collection(["apple", "banana", "cherry"])
        assert collection.exists(lambda x: x.startswith("a")) is True
        assert collection.exists(lambda x: x.startswith("z")) is False

    def test_exists_with_custom_objects(self):
        """Test exists() with custom objects."""

        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        people = Collection(
            [Person("Alice", 25), Person("Bob", 30), Person("Charlie", 35)]
        )

        assert people.exists(lambda p: p.name == "Bob") is True
        assert people.exists(lambda p: p.age > 30) is True
        assert people.exists(lambda p: p.name == "David") is False

    def test_exists_with_none_values(self):
        """Test exists() with None values in collection."""
        collection = Collection([1, None, 3, None, 5])
        assert collection.exists(lambda x: x is None) is True
        assert collection.exists(lambda x: x is not None) is True

    def test_exists_with_complex_predicates(self):
        """Test exists() with complex predicate functions."""
        collection = Collection([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Check for even numbers
        assert collection.exists(lambda x: x % 2 == 0) is True

        # Check for numbers divisible by 3
        assert collection.exists(lambda x: x % 3 == 0) is True

        # Check for prime numbers (simplified check)
        def is_prime(n):
            if n < 2:
                return False
            return all(n % i != 0 for i in range(2, int(n**0.5) + 1))

        assert collection.exists(is_prime) is True

    def test_exists_consistency_with_first(self):
        """Test that exists() is consistent with first() method."""
        collection = Collection([1, 2, 3, 4, 5])

        # Test with predicate
        def predicate(x):
            return x > 3

        assert collection.exists(predicate) == (collection.first(predicate) is not None)

        # Test without predicate
        assert collection.exists() == (collection.first() is not None)

    def test_exists_with_empty_collection_and_predicate(self):
        """Test exists() with predicate on empty collection."""
        collection = Collection()
        assert collection.exists(lambda x: x > 0) is False
