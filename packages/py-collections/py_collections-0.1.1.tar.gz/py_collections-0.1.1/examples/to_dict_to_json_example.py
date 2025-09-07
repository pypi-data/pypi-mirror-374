#!/usr/bin/env python3
"""
Example demonstrating the Collection to_dict and to_json methods.
"""

import json

from py_collections import Collection


def main():
    data = Collection(
        [
            {"name": "Alice", "age": 30},
            (1, 2, 3),
            {"tags": {"python", "collections"}},
        ]
    )

    # Convert to plain Python structures
    structure = data.to_dict()
    _ = structure

    # JSON-ready structure and string
    json_ready = data.to_dict(mode="json")
    json_str = data.to_json()

    # Demonstrate round-trip
    assert json.loads(json_str) == json_ready


if __name__ == "__main__":
    main()
