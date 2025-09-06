"""
Utility to persist a Python dictionary as JSON to disk.

This module exposes a single function, `save_dict_to_file`, which validates input
types, ensures the parent directory exists, and writes JSON with UTF-8 encoding.
It uses structured logging (no print statements) and surfaces clear exceptions.

The logger in this module does not configure any handlers by default (it only
attaches a NullHandler) to behave well inside libraries. Applications can
configure logging as needed.

Example:
    >>> from pathlib import Path
    >>> payload = {"name": "Ada", "skills": ["math", "logic"], "active": True}
    >>> out = Path("var/output/user.json")
    >>> save_dict_to_file(payload, out)  # no return value
    >>> out.exists()
    True

Test file:
    - Name pattern: ``test_save_dict_to_file.py`` (pytest or unittest compatible)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

# Library-friendly logging: do not configure global handlers here.
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def save_dict_to_file(data: dict[str, Any], filepath: str | Path) -> None:
    """Save a dictionary to a file in JSON format.

    The function accepts a string or :class:`pathlib.Path` for the destination,
    ensures parent directories exist, and writes pretty-printed JSON using UTF-8.

    Args:
        data: Dictionary to save. Values must be JSON-serializable.
        filepath: Destination file path (``str`` or :class:`pathlib.Path`).

    Raises:
        ValueError: If ``data`` is not a dictionary or contains values that are
            not JSON-serializable.
        TypeError: If ``filepath`` is not ``str`` or :class:`pathlib.Path`.
        OSError: If the function cannot create directories or write the file.

    Examples:
        Write to a new folder (folders will be created if missing):

        >>> save_dict_to_file({"a": 1}, "build/output.json")

        Using :class:`pathlib.Path`:

        >>> from pathlib import Path
        >>> save_dict_to_file({"ok": True}, Path("tmp/example.json"))

        Handling non-serializable values (raises ValueError):

        >>> import datetime as _dt
        >>> try:
        ...     save_dict_to_file({"when": _dt.datetime.now()}, "bad.json")
        ... except ValueError as exc:
        ...     "not JSON-serializable" in str(exc)
        True
    """
    # Validate input types early and log intent.
    if not isinstance(data, dict):
        raise ValueError("Input 'data' must be a dictionary.")

    if isinstance(filepath, str):
        path_obj = Path(filepath)
    elif isinstance(filepath, Path):
        path_obj = filepath
    else:
        raise TypeError("Parameter 'filepath' must be str or pathlib.Path.")

    LOGGER.debug("Preparing to save JSON. path=%s", path_obj)

    # Optional (non-fatal) hint via logging if the extension is unusual.
    if path_obj.suffix.lower() not in {".json", ""}:
        LOGGER.warning("Target file does not have a .json extension: %s", path_obj.name)

    # Ensure directories exist.
    try:
        parent = path_obj.parent
        if parent and not parent.exists():
            LOGGER.debug("Creating parent directories: %s", parent)
            parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        LOGGER.error("Failed to create directories for %s: %s", path_obj, exc)
        raise OSError(f"Failed to create directories for '{path_obj}': {exc}") from exc

    # Validate JSON-serializability before writing to avoid partial files.
    try:
        # This will raise TypeError for non-serializable objects.
        json.dumps(data)
    except TypeError as exc:
        LOGGER.error(
            "Provided data is not JSON-serializable. path=%s, error=%s",
            path_obj,
            exc,
        )
        raise ValueError("Input 'data' contains values that are not JSON-serializable.") from exc

    # Write atomically enough for typical cases (simple open/write).
    try:
        with path_obj.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.write("\n")  # POSIX-friendly newline at EOF
        LOGGER.info("Dictionary saved to %s", path_obj)
    except OSError as exc:
        LOGGER.error("Failed to write JSON to %s: %s", path_obj, exc)
        raise OSError(f"Failed to save the dictionary to '{path_obj}': {exc}") from exc
