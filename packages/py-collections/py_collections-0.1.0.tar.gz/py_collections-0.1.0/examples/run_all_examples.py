#!/usr/bin/env python3
"""
Script to run all Collection examples sequentially.
"""

import subprocess
import sys
from pathlib import Path


def run_example(example_file: str):
    """Run a single example file."""

    try:
        result = subprocess.run(
            [sys.executable, example_file],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.returncode == 0:
            pass
        else:
            pass

    except Exception:
        pass


def main():
    """Run all example files."""
    examples_dir = Path(__file__).parent

    # List of example files to run (in order)
    example_files = [
        "init_example.py",
        "append_example.py",
        "first_last_example.py",
        "first_with_predicate_example.py",
        "exists_example.py",
        "all_example.py",
        "generic_types_example.py",
        "edge_cases_example.py",
        "comprehensive_example.py",
        "typed_collections.py",
    ]

    for example_file in example_files:
        file_path = examples_dir / example_file
        if file_path.exists():
            run_example(example_file)
        else:
            pass


if __name__ == "__main__":
    main()
