"""Tools to analyze metadata from PyPI."""

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from attrs import asdict, frozen

from repute import requirements
from repute.cache import Cache
from repute.data import INDEX, Package
from repute.pypi.web import CACHE_DIR, download_pypi_data


@frozen(kw_only=True)
class Data:
    """Metadata for a PyPI package."""

    name: str
    version: str
    release_timestamp: datetime | None = None
    license: str | None = None
    github_url: str | None = None
    home_page: str | None = None
    author: str | None = None
    author_email: str | None = None
    description: str | None = None
    record_timestamp: datetime

    @property
    def dict(self) -> dict[str, str]:
        """Dictionary representation of the package."""
        return asdict(self)


def extract_release_timestamp(package: Package, data: dict[str, Any]) -> datetime:
    """Extract the release date for a specific version of a package.

    Args:
        package: Name and version of the package
        data: The pypi json data (as dictionary) for the package
    """
    version = package.version
    on_failure_msg = f"No release files found for {package.name}=={package.version}"
    if version == "latest":
        release_files = data["urls"]
    elif "releases" in data:
        releases = data["releases"]
        if package.version in releases:
            release_files = releases[package.version]
        else:
            raise ValueError(on_failure_msg)
    elif "urls" in data:
        release_files = data["urls"]
    else:
        raise ValueError(on_failure_msg)
    any_release_file = release_files[0]
    release_timestamp_str = any_release_file["upload_time"]
    return datetime.fromisoformat(release_timestamp_str)


def extract_values(package: Package) -> Data:
    """Extract values of interest from the cached pypi data.

    Args:
        package: Package object.

    Returns:
        Data containing information about the package

    Raises:
        requests.exceptions.HTTPError: If the request fails
    """
    cache = Cache(directory=CACHE_DIR, package_id=str(package))
    data = cache.load()
    assert data is not None, f"Package {package} not found in cache"
    release_timestamp = extract_release_timestamp(package=package, data=data)

    info = data["info"]
    # Extract GitHub URL
    github_url = None
    project_urls = info.get("project_urls", {}) or {}

    # Look for GitHub URL in project_urls
    for url in project_urls.values():
        if url and "github.com" in url.lower():
            github_url = url
            break

    # If no GitHub URL found in project_urls, check home_page
    if not github_url and info.get("home_page"):
        if "github.com" in info["home_page"].lower():
            github_url = info["home_page"]

    return Data(
        name=package.name,
        version=package.version,
        record_timestamp=datetime.now(),
        release_timestamp=release_timestamp,
        github_url=github_url,
        home_page=info.get("home_page"),
        author=info.get("author"),
        author_email=info.get("author_email"),
        license=info.get("license"),
        description=info.get("summary"),
    )


def derive_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive features from the raw pypi metadata.

    Args:
        df: Raw pypi metadata

    Returns: A table of derived pypi features indexed by package (name, version)
    """
    df["version_age_days"] = (df["record_timestamp"] - df["release_timestamp"]).dt.days
    df["time_since_last_release_days"] = (datetime.now() - df["latest_release_timestamp"]).dt.days
    return df


def get_features(packages: list[Package]) -> pd.DataFrame:
    """Get relevant pypi metadata for a list of packages.

    Args:
        packages: A list of Package objects (each having `.package_name` and `.version` attributes)

    Returns: A table of pypi features indexed by package (name, version)
    """
    latest_packages = [Package(name=package.name, version="latest") for package in packages]
    download_pypi_data(packages + latest_packages)
    df = pd.DataFrame([extract_values(item).dict for item in packages]).set_index("name").sort_index()
    df_latest = pd.DataFrame([extract_values(item).dict for item in latest_packages]).set_index("name").sort_index()
    assert df.index.equals(df_latest.index), "Index mismatch"
    df["latest_release_timestamp"] = df_latest["release_timestamp"]
    df = INDEX(df)
    return derive_features(df)


if __name__ == "__main__":
    # Example usage: `python repute/pypi/analytics.py`
    packages = requirements.parse(Path("demo/requirements.txt"))
    metadata = get_features(packages)
    print(f"Extracted metadata for {len(metadata)} packages:")
    print(metadata)
