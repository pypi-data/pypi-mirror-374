import json

import pytest

from py_collections.collection import Collection


class TestToDictToJson:
    def test_to_dict_primitives(self):
        c = Collection([1, 2.5, True, None, "x"])
        assert c.to_dict() == [1, 2.5, True, None, "x"]

    def test_to_dict_nested_containers(self):
        c = Collection(
            [
                {"a": 1, "b": [1, 2, {"c": 3}]},
                (1, 2),
                {1: "one"},
                {"set": {1, 2}},
            ]
        )

        result_default = c.to_dict()
        assert isinstance(result_default[0], dict)
        assert result_default[0]["b"][2]["c"] == 3
        assert isinstance(result_default[1], list)
        # default mode keeps non-string keys as-is
        assert 1 in result_default[2]
        # sets become lists
        assert isinstance(result_default[3]["set"], list)

        result_json = c.to_dict(mode="json")
        # json mode stringifies keys
        assert "1" in result_json[2]
        # sets still lists
        assert isinstance(result_json[3]["set"], list)

    def test_to_dict_dataclass_and_object(self):
        from dataclasses import dataclass

        @dataclass
        class D:
            x: int
            y: str

        class P:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        c = Collection([D(1, "a"), P("bob", 30)])
        r = c.to_dict()
        assert r[0] == {"x": 1, "y": "a"}
        assert r[1] == {"name": "bob", "age": 30}

    def test_to_dict_collection_inside(self):
        inner = Collection([1, 2])
        outer = Collection([inner, 3])
        assert outer.to_dict() == [[1, 2], 3]

    def test_to_dict_json_special_types(self):
        import datetime as dt
        import decimal as dec
        import uuid

        items = Collection(
            [
                dt.date(2020, 1, 2),
                dt.datetime(2020, 1, 2, 3, 4, 5),
                dt.time(3, 4, 5),
                dec.Decimal("1.23"),
                uuid.UUID("12345678-1234-5678-1234-567812345678"),
            ]
        )

        data = items.to_dict(mode="json")
        assert data[0] == "2020-01-02"
        assert data[1].startswith("2020-01-02T03:04:05")
        assert data[2].startswith("03:04:05")
        assert data[3] == 1.23
        assert data[4] == "12345678-1234-5678-1234-567812345678"

    def test_to_json_roundtrip(self):
        c = Collection([{"a": 1}, {"b": {"c": [1, 2]}}])
        s = c.to_json()
        assert isinstance(s, str)
        loaded = json.loads(s)
        assert loaded == c.to_dict(mode="json")

    def test_pydantic_models_if_available(self):
        try:
            from pydantic import BaseModel  # type: ignore
        except Exception:
            return

        class User(BaseModel):
            id: int
            name: str

        c = Collection([User(id=1, name="Alice")])
        d = c.to_dict()
        assert d == [{"id": 1, "name": "Alice"}]

        dj = c.to_dict(mode="json")
        assert dj == [{"id": 1, "name": "Alice"}]

        js = c.to_json()
        assert json.loads(js) == dj

    def test_to_dict_circular_references(self):
        """Test circular reference handling."""
        # Create circular reference
        a = Collection([1, 2])
        b = Collection([3, 4])
        a.append(b)
        b.append(a)

        result = a.to_dict()
        # The circular reference should be detected and marked as "[Circular]"
        # The actual result shows the circular reference is detected at the deepest level
        assert result == [1, 2, [3, 4, [1, 2, "[Circular]"]]]

    def test_to_dict_json_mode_duplicate_keys(self):
        """Test duplicate key detection in JSON mode."""
        # Create a dict with keys that would become the same string
        data = Collection([{1: "one", "1": "one_string"}])

        with pytest.raises(
            ValueError, match="Duplicate key after JSON stringification"
        ):
            data.to_dict(mode="json")

    def test_to_dict_json_mode_special_key_types(self):
        """Test JSON mode with special key types."""
        import datetime as dt
        import decimal as dec
        import uuid

        # Test with various key types that need special handling
        data = Collection(
            [
                {
                    dt.date(2020, 1, 1): "date_key",
                    dt.datetime(2020, 1, 1, 12, 0, 0): "datetime_key",
                    dt.time(12, 0, 0): "time_key",
                    uuid.UUID("12345678-1234-5678-1234-567812345678"): "uuid_key",
                    dec.Decimal("1.23"): "decimal_key",
                    None: "null_key",
                    (1, 2): "tuple_key",  # Will be converted to string
                }
            ]
        )

        result = data.to_dict(mode="json")
        assert isinstance(result[0], dict)
        # Keys should be converted to strings
        assert "2020-01-01" in result[0]
        assert "2020-01-01T12:00:00" in result[0]
        assert "12:00:00" in result[0]
        assert "12345678-1234-5678-1234-567812345678" in result[0]
        assert "1.23" in result[0]
        assert "null" in result[0]
        assert "<tuple:(1, 2)>" in result[0]

    def test_to_dict_objects_with_to_dict_method(self):
        """Test objects that have a to_dict method."""

        class CustomObject:
            def __init__(self, value):
                self.value = value

            def to_dict(self):
                return {"custom_value": self.value}

        data = Collection([CustomObject("test")])
        result = data.to_dict()
        assert result == [{"custom_value": "test"}]

    def test_to_dict_objects_with_failing_to_dict_method(self):
        """Test objects with to_dict method that fails."""

        class FailingObject:
            def __init__(self, value):
                self.value = value

            def to_dict(self):
                raise ValueError("to_dict failed")

        data = Collection([FailingObject("test")])
        result = data.to_dict()
        # Should fall back to __dict__ representation
        assert result == [{"value": "test"}]

    def test_to_dict_pydantic_v1_dict_method(self):
        """Test Pydantic v1 models with dict() method."""
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("Pydantic not available")

        # Create a mock Pydantic v1 model that has dict() method
        class MockPydanticV1:
            def __init__(self, value):
                self.value = value

            def dict(self):
                return {"pydantic_v1_value": self.value}

        data = Collection([MockPydanticV1("test")])
        result = data.to_dict()
        assert result == [{"pydantic_v1_value": "test"}]

    def test_to_dict_pydantic_v2_model_dump_with_mode_error(self):
        """Test Pydantic v2 model_dump with TypeError (older signature)."""
        try:
            from pydantic import BaseModel
        except ImportError:
            pytest.skip("Pydantic not available")

        # Create a mock that simulates older Pydantic v2 without mode parameter
        class MockPydanticV2Old:
            def __init__(self, value):
                self.value = value

            def model_dump(self, mode=None):
                if mode is not None:
                    raise TypeError("mode parameter not supported")
                return {"pydantic_v2_value": self.value}

        data = Collection([MockPydanticV2Old("test")])
        result = data.to_dict(mode="json")
        assert result == [{"pydantic_v2_value": "test"}]

    def test_to_dict_final_fallback_string_representation(self):
        """Test final fallback to string representation."""

        # Create an object that doesn't have __dict__ by using __slots__
        class NoDictObject:
            __slots__ = ["value"]

            def __init__(self, value):
                self.value = value

        data = Collection([NoDictObject("test")])
        result = data.to_dict()
        # Should fall back to string representation since it doesn't have __dict__
        assert isinstance(result[0], str)
        assert "NoDictObject" in result[0]

    def test_to_dict_hashable_check(self):
        """Test the is_hashable function with unhashable objects."""

        class UnhashableObject:
            __slots__ = ["value"]

            def __init__(self):
                self.value = "test"

            def __hash__(self):
                raise TypeError("unhashable type")

        # This should not crash and should handle the unhashable object
        data = Collection([UnhashableObject()])
        result = data.to_dict()
        assert len(result) == 1
        assert isinstance(result[0], str)  # Should fall back to string representation
