import pytest

from py_collections.collection import Collection


class TestDumpMe:
    def test_dump_me_with_empty_collection(self, capsys):
        """Test dump_me() with empty collection."""
        collection = Collection()
        collection.dump_me()

        captured = capsys.readouterr()
        output = captured.out

        assert "=== Collection Dump ===" in output
        assert "Collection: Collection([])" in output
        assert "Length: 0" in output
        assert "(empty collection)" in output
        assert "=== End Collection Dump ===" in output

    def test_dump_me_with_items(self, capsys):
        """Test dump_me() with items in collection."""
        collection = Collection([1, "hello", 3.14])
        collection.dump_me()

        captured = capsys.readouterr()
        output = captured.out

        assert "=== Collection Dump ===" in output
        assert "Collection: Collection([1, 'hello', 3.14])" in output
        assert "Length: 3" in output
        assert "[0]: 1 (type: int)" in output
        assert "[1]: hello (type: str)" in output
        assert "[2]: 3.14 (type: float)" in output
        assert "=== End Collection Dump ===" in output

    def test_dump_me_does_not_stop_execution(self):
        """Test that dump_me() does not stop execution."""
        collection = Collection([1, 2, 3])

        # Should not raise SystemExit
        collection.dump_me()

        # Execution should continue
        assert len(collection) == 3

    def test_dump_me_and_die_with_empty_collection(self, capsys):
        """Test dump_me_and_die() with empty collection."""
        collection = Collection()

        with pytest.raises(
            SystemExit, match="Collection dump completed - execution stopped"
        ):
            collection.dump_me_and_die()

        captured = capsys.readouterr()
        output = captured.out

        assert "=== Collection Dump ===" in output
        assert "Collection: Collection([])" in output
        assert "Length: 0" in output
        assert "(empty collection)" in output
        assert "=== End Collection Dump ===" in output

    def test_dump_me_and_die_with_items(self, capsys):
        """Test dump_me_and_die() with items in collection."""
        collection = Collection([1, "hello", 3.14])

        with pytest.raises(
            SystemExit, match="Collection dump completed - execution stopped"
        ):
            collection.dump_me_and_die()

        captured = capsys.readouterr()
        output = captured.out

        assert "=== Collection Dump ===" in output
        assert "Collection: Collection([1, 'hello', 3.14])" in output
        assert "Length: 3" in output
        assert "[0]: 1 (type: int)" in output
        assert "[1]: hello (type: str)" in output
        assert "[2]: 3.14 (type: float)" in output
        assert "=== End Collection Dump ===" in output

    def test_dump_me_and_die_stops_execution(self):
        """Test that dump_me_and_die() stops execution."""
        collection = Collection([1, 2, 3])

        with pytest.raises(SystemExit):
            collection.dump_me_and_die()

    def test_dump_me_and_die_uses_dump_me(self, capsys):
        """Test that dump_me_and_die() uses dump_me() internally."""
        collection = Collection([1, 2, 3])

        # First call dump_me directly
        collection.dump_me()
        captured1 = capsys.readouterr()
        output1 = captured1.out

        # Then call dump_me_and_die
        with pytest.raises(SystemExit):
            collection.dump_me_and_die()
        captured2 = capsys.readouterr()
        output2 = captured2.out

        # Both should produce the same output (before the SystemExit)
        assert output1 == output2

    def test_dump_me_with_complex_objects(self, capsys):
        """Test dump_me() with complex objects."""

        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        people = Collection([Person("Alice", 25), Person("Bob", 30)])

        people.dump_me()
        captured = capsys.readouterr()
        output = captured.out

        assert "=== Collection Dump ===" in output
        assert "Length: 2" in output
        assert "[0]: " in output
        assert "[1]: " in output
        assert "type: Person" in output
