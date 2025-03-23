"""Tools to fetch metadata from PyPI."""

from datetime import datetime
from typing import Any

import requests
from attrs import define, field, frozen

from repute import constants, requirements
from repute.cache import CachedClient

CACHE_DIR = constants.CACHE_DIR / "pypi"
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


@define
class CachedPyPIClient(CachedClient):
    """Client for interacting with the PyPI API with caching."""

    client: Client = field(factory=Client)

    def get_package_data(self, package: requirements.Package) -> dict[str, Any]:
        """Get data for a package from PyPI.

        Args:
            package: Package to fetch data for

        Returns:
            The package data from PyPI
        """
        return self.get_cached_data(
            package_id=str(package),
            fetch_func=lambda: self.client(package_name=package.name, version=package.version),
        )


def download_pypi_data(
    packages: list[requirements.Package],
    max_request_per_second: int = 10,
    cache_duration_days: int = constants.DEFAULT_CACHE_DURATION_DAYS,
) -> None:
    """Get metadata for multiple packages.

    Args:
        packages: A list of Package objects (each having `.package_name` and `.version` attributes)
        max_request_per_second: Maximum number of requests to make per second, to avoid negative attention from PyPI
        cache_duration_days: Number of days to keep a package's cached data before refreshing it
    """
    client = CachedPyPIClient(
        cache_dir=CACHE_DIR,
        max_request_per_second=max_request_per_second,
        cache_duration_days=cache_duration_days,
    )

    for package in packages:
        client.get_package_data(package)
