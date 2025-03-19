"""Inference of github URLs based on PyPI data."""

import re
from typing import Any

from repute.constants import GH_URL_BASE


def run_url_regex(text: str) -> str | None:
    """Find the first URL containing 'github.com/username/repository' in a given text string.

    Args:
        text (str): The text to search in.

    Returns:
        str or None: The first GitHub repository URL found in the text, or None if no match found.
    """
    pattern = r'https?://(?:www\.)?github\.com/[^/\s<>"\'()]+/[^/\s<>"\'()][^/\s<>"\'()]*'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def infer_github_url(*, name: str, info: dict[str, Any]) -> str | None:
    """Get the GitHub URL from the PyPI metadata.

    Args:
        name: Name of the package
        info: PyPI metadata for the package
    """

    # Try to find the GitHub repo URL in project_urls
    urls = info.get("project_urls", {}) or {}
    urls = {key.lower(): value for key, value in urls.items()}
    url_key_precedence = [
        "github",
        "source",
        "repository",
        "code",
        "homepage",
        "download",
        "source code",
        "repository",
        "changelog",
    ]
    for url_key in url_key_precedence:
        url = urls.pop(url_key, None)
        if url and GH_URL_BASE in url:
            return url

    # Check remaining project_urls for obvious GitHub URLs
    for url in urls.values():
        if GH_URL_BASE in url and name in url:
            return url

    # If no GitHub URL found in project_urls, check home_page
    home_page = info.get("home_page")
    if home_page:
        if GH_URL_BASE in home_page.lower():
            return home_page

    # Grep for GitHub URLs in the description
    url = run_url_regex(info.get("description", ""))
    if url and GH_URL_BASE in url and name in url:
        return url

    return None
