from py_collections.collection import Collection


class TestBefore:
    def test_before_empty_collection(self):
        """Test before with an empty collection."""
        collection = Collection()
        result = collection.before(3)
        assert result is None

    def test_before_element_not_found(self):
        """Test before when the target element is not found."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.before(10)
        assert result is None

    def test_before_first_element(self):
        """Test before when target is the first element."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.before(1)
        assert result is None

    def test_before_middle_element(self):
        """Test before with an element in the middle."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.before(3)
        assert result == 2

    def test_before_last_element(self):
        """Test before with the last element."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.before(5)
        assert result == 4

    def test_before_with_strings(self):
        """Test before with string elements."""
        collection = Collection(["a", "b", "c", "d", "e"])
        result = collection.before("c")
        assert result == "b"

    def test_before_with_mixed_types(self):
        """Test before with mixed type elements."""
        collection = Collection([1, "hello", 3.14, True, None])
        result = collection.before(3.14)
        assert result == "hello"

    def test_before_with_duplicates(self):
        """Test before with duplicate elements (should return before first occurrence)."""
        collection = Collection([1, 2, 3, 2, 4, 5])
        result = collection.before(2)
        assert result == 1  # Should return before the first occurrence of 2

    def test_before_with_predicate(self):
        """Test before with a predicate function."""
        collection = Collection([1, 2, 3, 4, 5, 6])
        result = collection.before(lambda x: x % 2 == 0)
        assert result == 1  # Before the first even number (2)

    def test_before_with_predicate_first_element(self):
        """Test before with predicate matching first element."""
        collection = Collection([2, 3, 4, 5, 6])
        result = collection.before(lambda x: x % 2 == 0)
        assert result is None  # First element is even, so no element before it

    def test_before_with_predicate_middle_element(self):
        """Test before with predicate matching middle element."""
        collection = Collection([1, 3, 4, 5, 7])
        result = collection.before(lambda x: x % 2 == 0)
        assert result == 3  # Before the first even number (4)

    def test_before_with_predicate_last_element(self):
        """Test before with predicate matching last element."""
        collection = Collection([1, 3, 5, 6])
        result = collection.before(lambda x: x % 2 == 0)
        assert result == 5  # Before the first even number (6)

    def test_before_with_predicate_no_match(self):
        """Test before with predicate that doesn't match any element."""
        collection = Collection([1, 3, 5, 7])
        result = collection.before(lambda x: x % 2 == 0)
        assert result is None

    def test_before_with_complex_predicate(self):
        """Test before with a more complex predicate."""
        collection = Collection(["apple", "banana", "cherry", "date", "elderberry"])
        result = collection.before(lambda s: len(s) > 5)
        assert result == "apple"  # Before the first string longer than 5 characters

    def test_before_with_none_element(self):
        """Test before with None as an element."""
        collection = Collection([1, 2, None, 4, 5])
        result = collection.before(None)
        assert result == 2

    def test_before_with_none_target(self):
        """Test before with None as the target."""
        collection = Collection([1, 2, None, 4, 5])
        result = collection.before(None)
        assert result == 2

    def test_before_single_element_collection(self):
        """Test before with a collection containing only one element."""
        collection = Collection([42])
        result = collection.before(42)
        assert result is None

    def test_before_two_elements(self):
        """Test before with a collection containing two elements."""
        collection = Collection([1, 2])
        result = collection.before(2)
        assert result == 1

        result = collection.before(1)
        assert result is None

    def test_before_with_custom_objects(self):
        """Test before with custom objects."""

        class TestObject:
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                if isinstance(other, TestObject):
                    return self.value == other.value
                return False

        obj1 = TestObject(1)
        obj2 = TestObject(2)
        obj3 = TestObject(3)

        collection = Collection([obj1, obj2, obj3])
        result = collection.before(obj3)
        assert result == obj2

    def test_before_with_predicate_returning_custom_objects(self):
        """Test before with predicate that matches custom objects."""

        class TestObject:
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                if isinstance(other, TestObject):
                    return self.value == other.value
                return False

        obj1 = TestObject(1)
        obj2 = TestObject(2)
        obj3 = TestObject(3)

        collection = Collection([obj1, obj2, obj3])
        result = collection.before(lambda obj: obj.value > 1)
        assert result == obj1  # Before the first object with value > 1
