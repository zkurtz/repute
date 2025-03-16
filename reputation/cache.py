"""Tools to cache metadata sources."""

# import time
# from datetime import datetime, timedelta
# from typing import Any, Literal

# from attrs import frozen
# from tqdm import tqdm

# from reputation import paths
# from reputation.data import Package
# from reputation.io import orjson as json_io

# CACHE_TIMESTAMP = "cache_timestamp"
# NOW = datetime.now()


# @frozen
# class PackageCache:
#     """IO wrapper for storing PyPI package metadata or a single package."""

#     directory: paths.Path
#     package_id: str

#     def __attrs_post_init__(self):
#         """Initialize the cache directory if it's not already there."""
#         self.directory.mkdir(parents=True, exist_ok=True)

#     @property
#     def path(self) -> paths.Path:
#         """Path to the cache file."""
#         return self.directory / f"{self.package_id}.json"

#     def load(self) -> dict[str, Any] | None:
#         """Try to load cached data for a package.

#         Returns:
#             Cached data or None if no cache is available found
#         """
#         if self.path.exists():
#             return json_io.load(self.path)
#         return None

#     def save(self, data: dict[str, Any]):
#         """Save data to the cache.

#         Args:
#             data: Data to cache
#         """
#         data[CACHE_TIMESTAMP] = datetime.now().isoformat()
#         json_io.save(data, self.path)


# @frozen
# class Downloader:
#     """Manage cache for multiple packages.

#     Attributes:
#         directory: Directory to store cache files
#         data_source: Name of the data source, like "pypi" or "github"
#     """

#     directory: paths.Path
#     data_source: Literal["pypi", "github"]
#     cache_duration_days: int = 30
#     max_request_per_second: int = 10

#     def __call__(self, packages: list[Package]) -> None:
#         """Get metadata for multiple packages.

#         Args:
#             packages: A list of Package objects (each having attributes `name`, `version`, and a `download` method)
#         """
#         for package in tqdm(packages, desc=f"Fetching {self.data_source} package data"):
#             cache = PackageCache(directory=self.directory, package_id=str(package))
#             data: dict[str, Any] | None = cache.load()
#             if data is not None:
#                 cache_timestamp = datetime.fromisoformat(data[CACHE_TIMESTAMP])
#                 if cache_timestamp < NOW - timedelta(days=self.cache_duration_days):
#                     data = None
#             if not data:
#                 time.sleep(1 / self.max_request_per_second)
#                 data = package.download()
#                 cache.save(data=data)
