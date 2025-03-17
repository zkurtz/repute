"""Tools to parse a requirements file."""

from pathlib import Path

import pandas as pd

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
    if not line or line.startswith("#"):
        return None
    if PIN_OPERATOR in line:
        package_name, version = line.split(PIN_OPERATOR)
        return Package(name=package_name, version=version)
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
