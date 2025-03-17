"""Tools to manage cache."""

from datetime import datetime
from typing import Any

from attrs import frozen
from dummio import orjson as json_io

from repute import paths

CACHE_TIMESTAMP = "cache_timestamp"


@frozen
class Cache:
    """IO wrapper for storing data or a single package."""

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
        json_io.save(data, filepath=self.path)
