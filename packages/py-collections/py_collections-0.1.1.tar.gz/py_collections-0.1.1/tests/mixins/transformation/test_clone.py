import pytest

from py_collections.collection import Collection


class TestClone:
    def test_clone_with_numbers(self):
        """Test cloning a collection of numbers."""
        original = Collection([1, 2, 3, 4, 5])
        cloned = original.clone()
        assert cloned.all() == [1, 2, 3, 4, 5]
        assert cloned is not original

    def test_clone_with_strings(self):
        """Test cloning a collection of strings."""
        original = Collection(["a", "b", "c", "d"])
        cloned = original.clone()
        assert cloned.all() == ["a", "b", "c", "d"]
        assert cloned is not original

    def test_clone_empty_collection(self):
        """Test cloning an empty collection."""
        original = Collection()
        cloned = original.clone()
        assert cloned.all() == []
        assert cloned is not original

    def test_clone_with_mixed_types(self):
        """Test cloning a collection with mixed types."""
        original = Collection([1, "hello", True, None, 3.14])
        cloned = original.clone()
        assert cloned.all() == [1, "hello", True, None, 3.14]
        assert cloned is not original

    def test_clone_with_complex_objects(self):
        """Test cloning a collection with complex objects."""
        original = Collection([{"a": 1}, {"b": 2}, {"c": 3}])
        cloned = original.clone()
        assert cloned.all() == [{"a": 1}, {"b": 2}, {"c": 3}]
        assert cloned is not original

    def test_clone_with_none_values(self):
        """Test cloning a collection with None values."""
        original = Collection([1, None, 3, None, 5])
        cloned = original.clone()
        assert cloned.all() == [1, None, 3, None, 5]
        assert cloned is not original

    def test_clone_with_duplicate_elements(self):
        """Test cloning a collection with duplicate elements."""
        original = Collection([1, 2, 2, 3, 2, 4])
        cloned = original.clone()
        assert cloned.all() == [1, 2, 2, 3, 2, 4]
        assert cloned is not original

    def test_clone_returns_new_collection(self):
        """Test that clone returns a new collection object."""
        original = Collection([1, 2, 3])
        cloned = original.clone()

        # They should be different objects
        assert cloned is not original
        # But have the same content
        assert cloned.all() == original.all()

    def test_clone_independence(self):
        """Test that cloned collection is independent of the original."""
        original = Collection([1, 2, 3])
        cloned = original.clone()

        # Modify the original
        original.append(4)
        assert original.all() == [1, 2, 3, 4]
        assert cloned.all() == [1, 2, 3]

        # Modify the clone
        cloned.append(5)
        assert original.all() == [1, 2, 3, 4]
        assert cloned.all() == [1, 2, 3, 5]

    def test_clone_with_large_collection(self):
        """Test cloning a larger collection."""
        original = Collection(list(range(1000)))
        cloned = original.clone()
        assert cloned.all() == list(range(1000))
        assert cloned is not original

    def test_clone_chaining(self):
        """Test chaining clone with other methods."""
        original = Collection([1, 2, 3, 4, 5])

        # Clone and then reverse
        cloned = original.clone().reverse()
        assert cloned.all() == [5, 4, 3, 2, 1]
        assert original.all() == [1, 2, 3, 4, 5]

        # Clone and then filter
        cloned = original.clone().filter(lambda x: x % 2 == 0)
        assert cloned.all() == [2, 4]
        assert original.all() == [1, 2, 3, 4, 5]

    def test_clone_multiple_times(self):
        """Test cloning multiple times."""
        original = Collection([1, 2, 3])

        clone1 = original.clone()
        clone2 = original.clone()
        clone3 = original.clone()

        # All clones should be different objects
        assert clone1 is not original
        assert clone2 is not original
        assert clone3 is not original
        assert clone1 is not clone2
        assert clone1 is not clone3
        assert clone2 is not clone3

        # All should have the same content
        assert clone1.all() == [1, 2, 3]
        assert clone2.all() == [1, 2, 3]
        assert clone3.all() == [1, 2, 3]

    def test_clone_with_mutable_objects(self):
        """Test cloning with mutable objects."""
        original = Collection([[1, 2], [3, 4], [5, 6]])
        cloned = original.clone()

        # Modify a mutable object in the original
        original.all()[0].append(7)
        assert original.all() == [[1, 2, 7], [3, 4], [5, 6]]
        assert cloned.all() == [[1, 2, 7], [3, 4], [5, 6]]

        # This is expected behavior since we're copying references to mutable objects

    def test_clone_preserves_order(self):
        """Test that clone preserves the order of elements."""
        original = Collection([3, 1, 4, 1, 5, 9, 2, 6])
        cloned = original.clone()
        assert cloned.all() == [3, 1, 4, 1, 5, 9, 2, 6]

    def test_clone_with_custom_objects(self):
        """Test cloning with custom objects."""

        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

            def __eq__(self, other):
                return self.name == other.name and self.age == other.age

        original = Collection([Person("Alice", 30), Person("Bob", 25)])
        cloned = original.clone()
        assert cloned.all() == [Person("Alice", 30), Person("Bob", 25)]
        assert cloned is not original

    def test_clone_after_modifications(self):
        """Test cloning after the original has been modified."""
        original = Collection([1, 2, 3])
        original.append(4)
        original.remove(2)

        cloned = original.clone()
        assert cloned.all() == [1, 3, 4]
        assert cloned is not original
