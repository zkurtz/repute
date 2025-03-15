"""IO wrappers for orjson."""

from pathlib import Path
from typing import Any

import orjson


def save(data: dict[str, Any], filepath: Path):
    """Save data to a file using orjson.

    Args:
        data: Data to save
        filepath: Path to the file
    """
    with open(filepath, "wb") as file:
        file.write(orjson.dumps(data))


def load(filepath: Path) -> dict[str, Any]:
    """Load data from a file using orjson.

    Args:
        filepath: Path to the file

    Returns:
        Loaded data
    """
    with open(filepath, "rb") as file:
        return orjson.loads(file.read())
