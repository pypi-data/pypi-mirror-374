# read_json_file.py
"""
read_json_file
==============

Utility for safely reading a JSON file into a Python dictionary.

This module exposes a single function, `read_json_file`, which loads and
validates a JSON file from disk. It provides robust error handling and
structured logging to help diagnose common issues such as missing files,
invalid JSON syntax, or unexpected top-level JSON types.

Logging practices:
- A module-level logger is created with `__name__`.
- The function logs meaningful events at appropriate levels (INFO, ERROR).
- This module does **not** configure handlers/levels; consumers should do so.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def read_json_file(filepath: str | Path) -> dict[str, Any]:
    """Read a JSON file from disk and return its contents as a dictionary.

    The function performs several safety checks:
      * Verifies the path exists and is a regular file (not a directory).
      * Parses the file as JSON using UTF-8 encoding.
      * Ensures the top-level JSON value is a mapping (``dict``). If the file
        contains a valid JSON value that is **not** a dictionary (e.g., a list
        or a string), a :class:`TypeError` is raised.

    This function uses structured logging for visibility and re-raises parsing
    errors with enhanced messages while preserving the original traceback
    context.

    Args:
        filepath: Path to the JSON file as a string or :class:`pathlib.Path`.

    Returns:
        A dictionary representing the top-level JSON object.

    Raises:
        FileNotFoundError: If the path does not exist.
        IsADirectoryError: If the path exists but is not a file.
        PermissionError: If the file cannot be opened due to permissions.
        json.JSONDecodeError: If the file contains invalid JSON.
        TypeError: If the top-level JSON value is not a dictionary.

    Examples:
        Read a valid JSON file:

        >>> # Suppose /tmp/config.json contains: {"debug": true, "port": 8080}
        >>> from read_json_file import read_json_file
        >>> data = read_json_file("/tmp/config.json")
        >>> data["port"]
        8080

        Handling errors:

        >>> try:
        ...     read_json_file("/not/there.json")
        ... except FileNotFoundError:
        ...     print("Missing file!")
        Missing file!

        Non-dict JSON:

        >>> # Suppose /tmp/list.json contains: [1, 2, 3]
        >>> read_json_file("/tmp/list.json")  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        TypeError: Expected top-level JSON object (dict), got list.
    """
    path = Path(filepath)

    # Existence check
    if not path.exists():
        logger.error("File not found: %s", path)
        raise FileNotFoundError(f"No such file: {path}")

    # Ensure it's a file, not a directory or special file
    if not path.is_file():
        logger.error("Path is not a file: %s", path)
        raise IsADirectoryError(f"Path is not a file: {path}")

    try:
        # Open using an explicit encoding to avoid platform-dependent defaults.
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

            # Validate the top-level structure early to avoid downstream surprises.
            if not isinstance(data, dict):
                logger.error(
                    "Unexpected JSON top-level type in %s: %s",
                    path,
                    type(data).__name__,
                )
                raise TypeError(
                    f"Expected top-level JSON object (dict), got {type(data).__name__}."
                )

            logger.info("Successfully read JSON file: %s", path)
            return data

    except PermissionError:
        # Preserve original stack plus add context to logs.
        logger.exception("Permission denied when accessing file: %s", path)
        raise

    except json.JSONDecodeError as e:
        # Log with structured details; e.lineno/e.colno are computed from e.pos.
        logger.error(
            "Invalid JSON in %s (line %s, column %s): %s",
            path,
            getattr(e, "lineno", "?"),
            getattr(e, "colno", "?"),
            e.msg,
        )
        # Re-raise with a richer message + preserve original context.
        raise json.JSONDecodeError(
            f"Error decoding JSON from file {path}: {e.msg}",
            e.doc,
            e.pos,
        ) from e


__all__ = ["read_json_file"]
