"""Tools to fetch metadata from PyPI."""

import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from attrs import asdict, field, frozen
from pandahandler.indexes import Index
from tqdm import tqdm

from reputation import paths, requirements
from reputation.data import Package
from reputation.io import orjson as json_io

CACHE_DIR = paths.CACHE_DIR / "pypi"
CACHE_TIMESTAMP = "cache_timestamp"
NOW = datetime.now()
INDEX = Index(
    names=[
        "name",
        "version",
    ]
)


@frozen
class Client:
    """Client for interacting with the PyPI API.

    Attributes:
        session: Requests session to use for API requests
        base_url: Base URL for the PyPI API
    """

    session: requests.Session = field(factory=requests.Session)
    base_url: str = "https://pypi.org/pypi"

    def __call__(self, package_name: str, version: str = "latest") -> dict[str, Any]:
        """Get the JSON data for a package from PyPI.

        Args:
            package_name: Name of the package
            version: Specific version to fetch; defaults to "latest"
        """
        # Build URL
        url = f"{self.base_url}/{package_name}"
        if version != "latest":
            url = f"{url}/{version}"
        url = f"{url}/json"

        # Make request
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return data


@frozen
class Cache:
    """IO wrapper for storing PyPI package metadata or a single package."""

    directory: paths.Path
    package_id: str

    def __attrs_post_init__(self):
        """Initialize the cache directory if it's not already there."""
        self.directory.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> paths.Path:
        """Path to the cache file."""
        return self.directory / f"{self.package_id}.json"

    def load(self) -> dict[str, Any] | None:
        """Try to load cached data for a package.

        Returns:
            Cached data or None if no cache is available found
        """
        if self.path.exists():
            return json_io.load(self.path)
        return None

    def save(self, data: dict[str, Any]):
        """Save data to the cache.

        Args:
            data: Data to cache
        """
        data[CACHE_TIMESTAMP] = datetime.now().isoformat()
        json_io.save(data, self.path)


def download_pypi_data(
    packages: list[requirements.Package],
    max_request_per_second: int = 10,
    cache_duration_days: int = 30,
) -> None:
    """Get metadata for multiple packages.

    Args:
        packages: A list of Package objects (each having `.package_name` and `.version` attributes)
        max_request_per_second: Maximum number of requests to make per second, to avoid negative attention from PyPI
        cache_duration_days: Number of days to keep a package's cached data before refreshing it
    """
    client = Client()
    for package in tqdm(packages, desc="Fetching PyPI package data"):
        cache = Cache(directory=CACHE_DIR, package_id=str(package))
        data: dict[str, Any] | None = cache.load()
        if data is not None:
            cache_timestamp = datetime.fromisoformat(data[CACHE_TIMESTAMP])
            if cache_timestamp < NOW - timedelta(days=cache_duration_days):
                data = None
        if not data:
            time.sleep(1 / max_request_per_second)
            data = client(package_name=package.name, version=package.version)
            cache.save(data=data)


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


def get_features(packages: list[Package]) -> pd.DataFrame:
    """Get relevant pypi metadata for a list of packages.

    Args:
        packages: A list of Package objects (each having `.package_name` and `.version` attributes)

    Returns: A table of pypi features indexed by package (name, version)
    """
    latest_packages = [Package(name=package.name, version="latest") for package in packages]

    df = pd.DataFrame([extract_values(item).dict for item in packages]).set_index("name").sort_index()
    df_latest = pd.DataFrame([extract_values(item).dict for item in latest_packages]).set_index("name").sort_index()
    assert df.index.equals(df_latest.index), "Index mismatch"
    df["days_prior_to_latest_release"] = (df_latest["release_timestamp"] - df["release_timestamp"]).dt.days
    df = INDEX(df)
    return df.sort_values("release_timestamp", ascending=False)


if __name__ == "__main__":
    # Example usage: `python reputation/pypi.py`
    packages = requirements.parse(Path("demo/requirements.txt"))
    metadata = get_features(packages)
    print(f"Extracted metadata for {len(metadata)} packages:")
    print(metadata)
