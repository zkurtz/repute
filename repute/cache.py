"""Tools to manage cache."""

import time
from datetime import datetime, timedelta
from typing import Any, Callable, TypeVar

from attrs import define, frozen
from dummio import orjson as json_io
from tqdm import tqdm

from repute import constants

CACHE_TIMESTAMP = "cache_timestamp"
LAST_REQUEST_TIME = "last_request_time"

T = TypeVar("T")


@frozen
class Cache:
    """IO wrapper for storing data or a single package."""

    directory: constants.Path
    package_id: str

    def __attrs_post_init__(self):
        """Initialize the cache directory if it's not already there."""
        self.directory.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> constants.Path:
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
        json_io.save(data, filepath=self.path)


@define
class CachedClient:
    """Base class for clients that need caching functionality.

    This class handles the common pattern of:
    1. Loading from cache
    2. Checking cache freshness
    3. Making API requests when needed
    4. Saving to cache
    """

    cache_dir: constants.Path
    max_request_per_second: int = 10
    cache_duration_days: int = constants.DEFAULT_CACHE_DURATION_DAYS

    def _rate_limit(self, cache: Cache) -> None:
        """Ensure we don't exceed the rate limit.

        Args:
            cache: Cache instance to store rate limiting state
        """
        data = cache.load() or {}
        last_request = data.get(LAST_REQUEST_TIME, 0)
        now = time.time()
        time_since_last = now - last_request
        if time_since_last < 1 / self.max_request_per_second:
            time.sleep(1 / self.max_request_per_second - time_since_last)
        data[LAST_REQUEST_TIME] = time.time()
        cache.save(data)

    def _is_cache_fresh(self, data: dict[str, Any]) -> bool:
        """Check if the cached data is fresh enough to use.

        Args:
            data: The cached data to check

        Returns:
            True if the cache is fresh, False otherwise
        """
        if data is None:
            return False
        cache_timestamp = datetime.fromisoformat(data[CACHE_TIMESTAMP])
        return cache_timestamp >= datetime.now() - timedelta(days=self.cache_duration_days)

    def get_cached_data(
        self,
        package_id: str,
        fetch_func: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        """Get data for a package, using cache if available and fresh.

        Args:
            package_id: Unique identifier for the package
            fetch_func: Function to fetch fresh data if cache is missing or stale

        Returns:
            The package data, either from cache or freshly fetched
        """
        cache = Cache(directory=self.cache_dir, package_id=package_id)
        data = cache.load()

        if not self._is_cache_fresh(data):
            self._rate_limit(cache)
            data = fetch_func()
            cache.save(data=data)

        return data

    def get_cached_data_batch(
        self,
        items: list[T],
        package_id_func: Callable[[T], str],
        fetch_func: Callable[[T], dict[str, Any]],
        desc: str = "Fetching data",
    ) -> dict[str, dict[str, Any]]:
        """Get data for multiple packages, using cache where possible.

        Args:
            items: List of items to fetch data for
            package_id_func: Function to get package_id from an item
            fetch_func: Function to fetch fresh data for an item
            desc: Description for the progress bar

        Returns:
            Dictionary mapping package IDs to their data
        """
        results = {}
        for item in tqdm(items, desc=desc):
            package_id = package_id_func(item)
            results[package_id] = self.get_cached_data(
                package_id=package_id,
                fetch_func=lambda: fetch_func(item),
            )
        return results
