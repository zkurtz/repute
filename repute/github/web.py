"""Tools to fetch star counts and other metadata from GitHub."""

import os
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import requests
from attrs import field, frozen
from tqdm import tqdm

from repute import constants
from repute.cache import CACHE_TIMESTAMP, Cache
from repute.github.data import GithubPackage

CACHE_DIR = constants.CACHE_DIR / "github"
NOW = datetime.now()


@frozen
class Client:
    """Client for interacting with the GitHub API.

    Attributes:
        session: Requests session to use for API requests
        base_url: Base URL for the GitHub API
        token: GitHub API token for authentication, if available
    """

    session: requests.Session = field(factory=requests.Session)
    base_url: str = "https://api.github.com"
    token: str | None = os.getenv("GITHUB_TOKEN")

    def __attrs_post_init__(self) -> None:
        """Set up the session with proper headers for GitHub API."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "repute-Tool",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        self.session.headers.update(headers)

    def __call__(self, package: GithubPackage) -> dict[str, Any]:
        """Get the repository data from GitHub.

        Args:
            package: A GithubPackage object
        """
        # Build URL
        url = f"{self.base_url}/repos/{package.repo_owner}/{package.repo_name}"

        # Make request
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


def download_github_data(
    packages: list[GithubPackage],
    cache_duration_days: int = 30,
) -> pd.DataFrame:
    """Get GitHub metadata for multiple packages.

    Args:
        packages: A list of Package objects
        cache_duration_days: Number of days to keep cached data before refreshing

    Returns:
        Dictionary mapping package IDs to their GitHub data
    """
    client = Client()
    results = []

    for package in tqdm(packages, desc="Fetching data from GitHub"):
        cache = Cache(directory=CACHE_DIR, package_id=str(package))
        data: dict[str, Any] | None = cache.load()
        if data is not None:
            cache_timestamp = datetime.fromisoformat(data[CACHE_TIMESTAMP])
            if cache_timestamp < NOW - timedelta(days=cache_duration_days):
                data = None

        if not data:
            try:
                data = client(package)
                cache.save(data=data)
            except requests.HTTPError as err:
                if err.response.status_code == 403:
                    msg = (
                        "Github API rate limit exceeded. Since responses are cached, just wait an hour and try again. "
                        "Or you may set the GITHUB_TOKEN environment variable to dramatically increase rate limits. "
                        "`repute` will automatically use GITHUB_TOKEN if it is set. "
                    )
                    raise RuntimeError(msg) from err
                if err.response.status_code == 404:
                    print(f"404 response from github for {package.name} with url {package.url}")
                else:
                    print(f"Error fetching GitHub data for {package.name}: {err}")
                continue

        # Store the result with star count prominently available
        values = {
            "name": package.name,
            "version": package.version,
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count"),
            "watchers": data.get("watchers_count"),
            "updated_at": data.get("updated_at"),
            "github_url": data.get("html_url"),
            "description": data.get("description"),
        }
        results.append(values)

    return pd.DataFrame(results)
