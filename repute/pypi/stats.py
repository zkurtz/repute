"""Wrap pypistats package to access pypi package download stats."""

import json
import time
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import pypistats
from tqdm import tqdm

from repute import constants
from repute.cache import CACHE_TIMESTAMP, Cache
from repute.data import Package

LOOKBACK_DAYS = 90
DATE_FMT = "%Y-%m-%d"
CACHE_DIR = constants.CACHE_DIR / "pypi_stats"
NOW = datetime.now()


def download_recent_download_counts(package: Package, lookback_days: int = LOOKBACK_DAYS) -> dict[str, int]:
    """Download the number of PYPI downloads (without mirrors) for a package in the last lookback_days days."""
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

    Returns: A pandas series of average daily download counts, indexed by package name
    """
    results = {}
    for package in tqdm(packages, desc="Fetching download stats from PyPI"):
        cache = Cache(directory=CACHE_DIR, package_id=str(package))
        data: dict[str, Any] | None = cache.load()
        if data is not None:
            cache_timestamp = datetime.fromisoformat(data[CACHE_TIMESTAMP])
            if cache_timestamp < NOW - timedelta(days=cache_duration_days):
                data = None
        if not data:
            time.sleep(1 / max_request_per_second)
            data = download_recent_download_counts(package)
            cache.save(data=data)
        results[package.name] = data["downloads"] / LOOKBACK_DAYS
    return pd.Series(results, name=f"avg_daily_downloads_last_{LOOKBACK_DAYS}_days")
