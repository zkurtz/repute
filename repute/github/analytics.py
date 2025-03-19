"""Generate metrics on github data sources."""

import pandas as pd

from repute.constants import GH_URL_BASE
from repute.data import INDEX
from repute.github.data import GithubPackage
from repute.github.web import download_github_data

SEP = "/"


def to_package(url: str, **kwargs) -> GithubPackage:
    """Construct a github package.

    Args:
        url: The URL of the package on GitHub
        **kwargs: Additional metadata for the package
    """
    if not url:
        raise ValueError("URL must be provided")
    null_package = GithubPackage(
        url=url,
        repo_owner=None,
        repo_name=None,
        **kwargs,
    )
    if GH_URL_BASE not in url:
        return null_package
    _, body = url.split(GH_URL_BASE)
    if SEP not in body:
        return null_package
    parts = body.split(SEP)
    repo_owner = parts[0]
    repo_name = parts[1]

    # remove any `.git` suffix on the repo name:
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    return GithubPackage(
        url=url,
        repo_owner=repo_owner,
        repo_name=repo_name,
        **kwargs,
    )


def get_features(urls: pd.Series) -> pd.DataFrame:
    """Get relevant pypi metadata for a list of packages.

    Args:
        packages: A list of Package objects (each having `.name` and `.version` attributes)
        urls: A series of URLs indexed by package (name, version)

    Returns: A table of pypi features indexed by package (name, version)
    """
    # construct gh_pkgs by iterating over urls using to_package, using the index of the series to set kwargs:
    gh_pkgs = [to_package(url, name=name, version=version) for (name, version), url in urls.to_dict().items()]
    df = download_github_data(gh_pkgs)
    return INDEX(df)
