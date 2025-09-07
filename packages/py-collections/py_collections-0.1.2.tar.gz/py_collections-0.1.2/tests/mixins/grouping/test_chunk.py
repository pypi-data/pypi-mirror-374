import pytest

from py_collections.collection import Collection


class TestChunk:
    def test_chunk_empty_collection(self):
        """Test chunking an empty collection."""
        collection = Collection()
        result = collection.chunk(3)
        assert result == []

    def test_chunk_size_one(self):
        """Test chunking with size 1."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.chunk(1)
        assert len(result) == 5
        assert result[0].all() == [1]
        assert result[1].all() == [2]
        assert result[2].all() == [3]
        assert result[3].all() == [4]
        assert result[4].all() == [5]

    def test_chunk_size_two(self):
        """Test chunking with size 2."""
        collection = Collection([1, 2, 3, 4, 5])
        result = collection.chunk(2)
        assert len(result) == 3
        assert result[0].all() == [1, 2]
        assert result[1].all() == [3, 4]
        assert result[2].all() == [5]

    def test_chunk_size_three(self):
        """Test chunking with size 3."""
        collection = Collection([1, 2, 3, 4, 5, 6])
        result = collection.chunk(3)
        assert len(result) == 2
        assert result[0].all() == [1, 2, 3]
        assert result[1].all() == [4, 5, 6]

    def test_chunk_size_larger_than_collection(self):
        """Test chunking with size larger than collection length."""
        collection = Collection([1, 2, 3])
        result = collection.chunk(5)
        assert len(result) == 1
        assert result[0].all() == [1, 2, 3]

    def test_chunk_size_equal_to_collection(self):
        """Test chunking with size equal to collection length."""
        collection = Collection([1, 2, 3])
        result = collection.chunk(3)
        assert len(result) == 1
        assert result[0].all() == [1, 2, 3]

    def test_chunk_with_strings(self):
        """Test chunking with string elements."""
        collection = Collection(["a", "b", "c", "d", "e"])
        result = collection.chunk(2)
        assert len(result) == 3
        assert result[0].all() == ["a", "b"]
        assert result[1].all() == ["c", "d"]
        assert result[2].all() == ["e"]

    def test_chunk_with_mixed_types(self):
        """Test chunking with mixed type elements."""
        collection = Collection([1, "a", 2.5, True, None])
        result = collection.chunk(2)
        assert len(result) == 3
        assert result[0].all() == [1, "a"]
        assert result[1].all() == [2.5, True]
        assert result[2].all() == [None]

    def test_chunk_invalid_size_zero(self):
        """Test chunking with size 0 raises ValueError."""
        collection = Collection([1, 2, 3])
        with pytest.raises(ValueError, match="Chunk size must be a positive integer"):
            collection.chunk(0)

    def test_chunk_invalid_size_negative(self):
        """Test chunking with negative size raises ValueError."""
        collection = Collection([1, 2, 3])
        with pytest.raises(ValueError, match="Chunk size must be a positive integer"):
            collection.chunk(-1)

    def test_chunk_invalid_size_float(self):
        """Test chunking with float size raises ValueError."""
        collection = Collection([1, 2, 3])
        with pytest.raises(ValueError, match="Chunk size must be a positive integer"):
            collection.chunk(2.5)

    def test_chunk_invalid_size_string(self):
        """Test chunking with string size raises ValueError."""
        collection = Collection([1, 2, 3])
        with pytest.raises(ValueError, match="Chunk size must be a positive integer"):
            collection.chunk("3")

    def test_chunk_result_types(self):
        """Test that chunk returns Collection instances."""
        collection = Collection([1, 2, 3, 4])
        result = collection.chunk(2)
        assert all(isinstance(chunk, Collection) for chunk in result)
        assert len(result) == 2
