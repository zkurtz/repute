"""Wrap pypistats package to access pypi package download stats."""

import json
from datetime import datetime, timedelta

import pandas as pd
import pypistats
from attrs import define, field, frozen

from repute import constants
from repute.cache import CachedClient
from repute.data import Package

LOOKBACK_DAYS = 90
DATE_FMT = "%Y-%m-%d"
CACHE_DIR = constants.CACHE_DIR / "pypi_stats"


@frozen
class Client:
    """Client for interacting with the PyPI stats API."""

    def __call__(self, package: Package, lookback_days: int = LOOKBACK_DAYS) -> dict[str, int]:
        """Get download stats for a package.

        Args:
            package: Package to get stats for
            lookback_days: Number of days to look back

        Returns:
            Dictionary containing download stats
        """
        end_date = datetime.now().strftime(DATE_FMT)
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime(DATE_FMT)
        downloads_str = pypistats.overall(
            package.name,
            mirrors=False,
            start_date=start_date,
            end_date=end_date,
            total="all",
            format="json",
        )
        assert isinstance(downloads_str, str), "Expected a string"
        downloads = json.loads(downloads_str)
        data = downloads["data"]
        assert len(data) == 1, "Expected a single data entry"
        entry = data[0]
        assert "downloads" in entry, "Expected 'downloads' key in data entry"
        return entry


@define
class CachedPyPIStatsClient(CachedClient):
    """Client for interacting with the PyPI stats API with caching."""

    client: Client = field(factory=Client)

    def get_package_data(self, package: Package) -> dict[str, int]:
        """Get download stats for a package.

        Args:
            package: Package to get stats for

        Returns:
            Dictionary containing download stats
        """
        return self.get_cached_data(
            package_id=str(package),
            fetch_func=lambda: self.client(package),
        )


def download_pypi_stats(
    packages: list[Package],
    max_request_per_second: int = 1,
    cache_duration_days: int = constants.DEFAULT_CACHE_DURATION_DAYS,
) -> pd.Series:
    """Get metadata for multiple packages.

    Args:
        packages: A list of Package objects (each having `.package_name` and `.version` attributes)
        max_request_per_second: Maximum number of requests to make per second, to avoid negative attention from PyPI
        cache_duration_days: Number of days to keep a package's cached data before refreshing it

    Returns: A pandas series of download counts indexed by package name
    """
    client = CachedPyPIStatsClient(
        cache_dir=CACHE_DIR,
        max_request_per_second=max_request_per_second,
        cache_duration_days=cache_duration_days,
    )

    results = {}
    for package in packages:
        data = client.get_package_data(package)
        results[package.name] = data["downloads"]
    return pd.Series(results)
