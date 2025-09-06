"""
Tests for save_dict_to_file using the standard library unittest.

File name structure requirement:
    - This file is named `test_save_dict_to_file.py` to be auto-discovered
      by pytest or unittest discovery (python -m unittest).

The tests avoid external dependencies and use a temporary directory.
"""

import json
import tempfile
import unittest
from pathlib import Path

# Import the function under test
from ebhkit.file import save_dict_to_file


class TestSaveDictToFile(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.base = Path(self.tmp_dir.name)

    def test_writes_json_file_and_creates_dirs(self) -> None:
        target = self.base / "nested" / "out.json"
        payload = {"x": 1, "y": [1, 2, 3], "ok": True}

        save_dict_to_file(payload, target)

        self.assertTrue(target.exists(), "Output file should exist.")
        with target.open("r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content, payload)

    def test_accepts_string_path(self) -> None:
        target = str(self.base / "strpath.json")
        save_dict_to_file({"a": "b"}, target)
        self.assertTrue(Path(target).exists())

    def test_rejects_non_dict_input(self) -> None:
        with self.assertRaises(ValueError):
            save_dict_to_file(["not", "a", "dict"], self.base / "bad.json")  # type: ignore[arg-type]

    def test_rejects_bad_path_type(self) -> None:
        with self.assertRaises(TypeError):
            save_dict_to_file({"a": 1}, 1234)  # type: ignore[arg-type]

    def test_non_serializable_value_raises_value_error(self) -> None:
        class NotSerializable:
            pass

        with self.assertRaises(ValueError):
            save_dict_to_file({"obj": NotSerializable()}, self.base / "bad.json")

    def test_writing_into_directory_fails(self) -> None:
        # Create a directory and try to write to it as if it were a file.
        target_dir = self.base / "adir"
        target_dir.mkdir(parents=True, exist_ok=True)

        # On most systems, opening a directory for writing as a file will raise
        #  OSError/IsADirectoryError.
        with self.assertRaises(OSError):
            save_dict_to_file({"k": "v"}, target_dir)

    def test_overwrites_existing_file(self) -> None:
        target = self.base / "overwrite.json"
        save_dict_to_file({"a": 1}, target)
        save_dict_to_file({"a": 2}, target)

        with target.open("r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content, {"a": 2})

    def test_adds_newline_at_eof(self) -> None:
        target = self.base / "newline.json"
        save_dict_to_file({"a": 1}, target)
        with target.open("rb") as f:
            data = f.read()
        self.assertTrue(data.endswith(b"\n"), "File should end with a newline.")


if __name__ == "__main__":
    # Allow running directly: python test_save_dict_to_file.py
    unittest.main(verbosity=2)
