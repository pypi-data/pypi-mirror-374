# tests_file_read_json_file.py
"""
Reference tests for read_json_file.read_json_file

This file name follows a pytest-friendly pattern: test_<module>.py

Run with:
    pytest -q
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pytest

# IMPORTANT: import the FUNCTION, not the module, to avoid "'module' object is not callable".
from ebhkit.file import read_json_file


@pytest.fixture(autouse=True)
def _configure_logging(caplog: pytest.LogCaptureFixture):
    """Configure logging for tests to capture this module's logs."""
    logging.basicConfig(level=logging.INFO)
    with caplog.at_level(logging.INFO, logger="read_json_file"):
        yield


def test_read_valid_json_returns_dict(tmp_path: Path):
    payload: dict[str, Any] = {"name": "service", "port": 8000, "debug": True}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(payload), encoding="utf-8")

    result = read_json_file(p)
    assert result == payload


def test_nonexistent_file_raises_file_not_found(tmp_path: Path):
    missing = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        read_json_file(missing)


def test_path_is_directory_raises_is_a_directory_error(tmp_path: Path):
    directory = tmp_path / "configs"
    directory.mkdir(parents=True, exist_ok=True)
    with pytest.raises(IsADirectoryError):
        read_json_file(directory)


def test_invalid_json_raises_json_decode_error(tmp_path: Path):
    bad = tmp_path / "invalid.json"
    bad.write_text("{ invalid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        read_json_file(bad)


def test_non_dict_json_raises_type_error(tmp_path: Path):
    arr_file = tmp_path / "array.json"
    arr_file.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(TypeError) as excinfo:
        read_json_file(arr_file)
    assert "Expected top-level JSON object (dict)" in str(excinfo.value)


def test_permission_error_is_logged_and_raised(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    target = tmp_path / "perm.json"
    target.write_text("{}", encoding="utf-8")

    original_open = Path.open

    def fake_open(self: Path, mode: str = "r", encoding: str | None = None):
        if self == target:
            raise PermissionError("Simulated permission denied")
        return original_open(self, mode, encoding=encoding)

    monkeypatch.setattr(Path, "open", fake_open, raising=True)

    with pytest.raises(PermissionError):
        read_json_file(target)
