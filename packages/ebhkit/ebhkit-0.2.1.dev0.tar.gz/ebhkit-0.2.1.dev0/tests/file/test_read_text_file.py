"""
Unit tests for the `read_text_file` function.

Run with:
    python -m pytest -q
or:
    python -m unittest tests.test_read_text_file -v
"""

import tempfile
import unittest
from pathlib import Path

from ebhkit.file import read_text_file


class TestReadTextFile(unittest.TestCase):
    """Unit tests for read_text_file."""

    def test_reads_existing_utf8_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.txt"
            expected = "hello\nworld\näöüß\n"
            path.write_text(expected, encoding="utf-8")
            self.assertEqual(read_text_file(path), expected)

    def test_raises_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "missing.txt"
            with self.assertRaises(FileNotFoundError):
                read_text_file(path)

    def test_raises_on_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)  # This is a directory
            with self.assertRaises(IsADirectoryError):
                read_text_file(path)

    def test_type_validation(self) -> None:
        with self.assertRaises(TypeError):
            read_text_file(123)  # type: ignore[arg-type]

    def test_unicode_decode_error(self) -> None:
        # Create a file with bytes invalid for UTF-8 (ISO-8859-1 encoded)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "latin1.txt"
            # 0xE9 (é) in Latin-1 is invalid as a standalone byte in UTF-8.
            with path.open("wb") as f:
                f.write(b"\xe9abc")
            with self.assertRaises(UnicodeDecodeError):
                read_text_file(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
