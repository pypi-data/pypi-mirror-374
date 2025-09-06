import logging
from pathlib import Path

# Library logging best practice: do not configure logging in a package.
# Attach a NullHandler so importing applications won't see "No handler found" warnings.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def read_text_file(filepath):
    """
    Reads the contents of a text file safely.

    Args:
        filepath (str | Path):
        The path to the text file. Can be either a string or a pathlib.Path object.

    Returns:
        str: The full contents of the file as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the provided path is a directory instead of a file.
        UnicodeDecodeError: If the file cannot be decoded with UTF-8 encoding.
        OSError: For other OS-related errors when trying to access the file.
    """
    try:
        # Ensure filepath is a Path object (works with both str and Path)
        filepath = Path(filepath)

        if filepath.is_dir():
            raise IsADirectoryError(f"Expected a file but got a directory: {filepath}")

        # Open the file with UTF-8 encoding in read mode
        with filepath.open("r", encoding="utf-8") as f:
            return f.read()

    except FileNotFoundError as err:
        raise FileNotFoundError(f"File not found: {filepath}") from err

    except IsADirectoryError as err:
        raise IsADirectoryError(f"Expected a file but got a directory: {filepath}") from err

    except UnicodeDecodeError as err:
        raise UnicodeDecodeError("utf-8", b"", 0, 1, f"Cannot decode file: {filepath}") from err

    except OSError as err:
        raise OSError(f"Error accessing file {filepath}: {err}") from err


__all__ = ["read_text_file"]
