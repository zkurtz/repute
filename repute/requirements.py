"""Tools to parse a requirements file."""

import warnings
from pathlib import Path

import pandas as pd
from packaging.requirements import Requirement

from repute.data import Package

PIN_OPERATOR = "=="


def parseline(line: str) -> Package | None:
    """Parse a line from a requirements file into a package name and version.

    Args:
        line (str): A line from a requirements file

    Returns:
        tuple[str, str]: A tuple where the first element is the package name and the second is the package version

    Raises:
        ValueError: If the line doesn't contain a package name and version
    """
    line = line.strip()
    if not line:
        return None
    if line.startswith("#"):
        return None
    if line.startswith("-e"):
        warnings.warn(f"ignoring editable installation: '{line}'")
        return None
    if line.startswith("-r"):
        raise ValueError(f"requirements file inclusions are not supported: '{line}'")

    if PIN_OPERATOR in line:
        # Remove inline comments (standard for requirements files to have comments on separate lines,
        # but we handle them for robustness)
        # Only remove comments that are not within quotes (environment markers use quotes)
        comment_pos = line.find("#")
        if comment_pos != -1:
            # Simple heuristic: if there's a semicolon before the #, it's likely in a marker
            semicolon_pos = line.find(";")
            if semicolon_pos == -1 or comment_pos < semicolon_pos:
                line = line[:comment_pos].strip()

        # Use packaging library to properly parse requirements with markers
        req = Requirement(line)
        # Check if the requirement has a pinned version using ==
        for spec in req.specifier:
            if spec.operator == PIN_OPERATOR:
                return Package(name=req.name, version=spec.version)
        # If we get here, there's a == but not in the version specifier
        raise ValueError(f"Unable to parse '{line}' as a package and version")
    else:
        raise ValueError(f"Unable to parse '{line}' as a package and version")


def parse(filepath: Path) -> list[Package]:
    """Parse a requirements.txt file to get a list of packages and their versions.

    Supports only fully-pinned package versions (using ==).

    Args:
        filepath: Path to the requirements.txt file
    """
    content = filepath.read_text()
    parsed_lines: list[Package | None] = [parseline(line) for line in content.splitlines()]
    return [item for item in parsed_lines if item is not None]


if __name__ == "__main__":
    # Run example usage as `python repute/requirements.py`
    data = parse(Path("demo/requirements.txt"))
    df = pd.DataFrame([item.dict for item in data])  # .set_index("name")["version"]
    print(df)
