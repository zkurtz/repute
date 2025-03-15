"""Tools to fetch metadata from PyPI."""

import time
from datetime import datetime, timedelta
from typing import Any

import requests
from attrs import field, frozen
from tqdm import tqdm

from reputation import paths, requirements
from reputation.data import Package
from reputation.io import orjson as json_io

CACHE_DIR = paths.CACHE_DIR / "pypi"
CACHE_TIMESTAMP = "cache_timestamp"
NOW = datetime.now()


@frozen
class PyPIClient:
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


def build_packages_data(packages: list[requirements.Package]) -> None:
    """Get metadata for multiple packages.

    Args:
        packages: A list of Package objects (each having `.package_name` and `.version` attributes)
    """
    client = PyPIClient()
    for package in tqdm(packages, desc="Fetching PyPI package data"):
        cache = Cache(directory=CACHE_DIR, package_id=str(package))
        data: dict[str, Any] | None = cache.load()
        if data is not None:
            cache_timestamp = datetime.fromisoformat(data[CACHE_TIMESTAMP])
            if cache_timestamp < NOW - timedelta(days=30):
                data = None
        if not data:
            # For rate limiting, we can add a sleep here:
            time.sleep(0.1)
            data = client(package_name=package.name, version=package.version)
            cache.save(data=data)


@frozen(kw_only=True)
class Data:
    """Metadata for a PyPI package."""

    name: str
    version: str
    record_timestamp: datetime
    release_date: datetime | None = None
    github_url: str | None = None
    home_page: str | None = None
    author: str | None = None
    author_email: str | None = None
    license: str | None = None
    description: str | None = None


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
    version = package.version
    info = data["info"]
    release_date = None
    if "releases" in data:
        releases = data["releases"]
        breakpoint()
        if version in releases:
            version = releases[version]
            if version:
                # Use the first release file's upload time
                release_date_str = version[0]["upload_time"]
                release_date = datetime.fromisoformat(release_date_str)
    elif "urls" in data:
        urls = data["urls"]
        breakpoint()
        if urls:
            # If we don't have 'releases', try to get release date from 'urls'
            release_date_str = urls[0]["upload_time"]
            release_date = datetime.fromisoformat(release_date_str)
    else:
        raise ValueError(f"No release data found for {package}")

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
        release_date=release_date,
        github_url=github_url,
        home_page=info.get("home_page"),
        author=info.get("author"),
        author_email=info.get("author_email"),
        license=info.get("license"),
        description=info.get("summary"),
    )


if __name__ == "__main__":
    # Example usage: `python reputation/pypi.py`
    from pathlib import Path

    data = requirements.parse(Path("demo/requirements.txt"))
    build_packages_data(data)
    metadata = [extract_values(item) for item in data]
    breakpoint()
    print(metadata)
