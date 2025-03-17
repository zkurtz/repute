"""Tools to fetch metadata from PyPI."""

import time
from datetime import datetime, timedelta
from typing import Any

import requests
from attrs import field, frozen
from tqdm import tqdm

from repute import paths, requirements
from repute.cache import CACHE_TIMESTAMP, Cache

CACHE_DIR = paths.CACHE_DIR / "pypi"
NOW = datetime.now()


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
