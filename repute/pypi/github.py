"""Inference of github URLs based on PyPI data."""

import re
from typing import Any

from repute.constants import GH_URL_BASE

KNOWN_PROJECTS_NOT_ON_GITHUB = {
    "beautifulsoup4",  # https://launchpad.net/beautifulsoup/
    "et-xmlfile",  # https://foss.heptapod.net/openpyxl/et_xmlfile
    "openpyxl",  # https://foss.heptapod.net/openpyxl/openpyxl/
    "ruamel-yaml",  # https://sourceforge.net/projects/ruamel-yaml/
    "ruamel-yaml-clib",  # https://sourceforge.net/projects/ruamel-yaml/
    # NVIDIA CUDA proprietary binary distributions (no public GitHub repos)
    "nvidia-cublas-cu12",
    "nvidia-cuda-cupti-cu12",
    "nvidia-cuda-nvrtc-cu12",
    "nvidia-cuda-runtime-cu12",
    "nvidia-cudnn-cu12",
    "nvidia-cufft-cu12",
    "nvidia-cufile-cu12",
    "nvidia-curand-cu12",
    "nvidia-cusolver-cu12",
    "nvidia-cusparse-cu12",
    "nvidia-cusparselt-cu12",
    "nvidia-nccl-cu12",
    "nvidia-nvjitlink-cu12",
    "nvidia-nvtx-cu12",
}
MANUAL_GITHUB_URLS: dict[str, str] = {
    "jupyter": "https://github.com/jupyter/jupyter",
    "jupyter-console": "https://github.com/jupyter/jupyter_console",
    "jupyter-server-terminals": "https://github.com/jupyter/jupyter_server_terminals",
    "notebook-shim": "https://github.com/jupyter/notebook_shim",
    "numba": "https://github.com/numba/numba",
    "protobuf": "https://github.com/protocolbuffers/protobuf",
    "pydub": "https://github.com/jiaaro/pydub",
    "pywinpty": "https://github.com/andfoy/pywinpty",
    "sigtools": "https://github.com/epsy/sigtools",
    "solara-server": "https://github.com/widgetti/solara",
    "solara-ui": "https://github.com/widgetti/solara",
    "sortedcontainers": "https://github.com/grantjenks/python-sortedcontainers",
    "uri-template": "https://github.com/python-hyper/uritemplate",
    "widgetsnbextension": "https://github.com/jupyter-widgets/ipywidgets",
}


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
    if name in MANUAL_GITHUB_URLS:
        return MANUAL_GITHUB_URLS[name]
    if name in KNOWN_PROJECTS_NOT_ON_GITHUB:
        return None

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
    description: str = info.get("description", "").lower()
    url = run_url_regex(description)
    if url and GH_URL_BASE in url and name in url:
        return url

    if f"launchpad.net/{name}" in description.lower():
        # hosted on launchpad instead of github
        return None

    return None
