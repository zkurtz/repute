"""Generate metrics on github data sources."""

import pandas as pd

from repute.data import INDEX, Package
from repute.github.data import GithubPackageConstructor
from repute.github.web import download_github_data


def get_features(packages: list[Package], *, urls: pd.Series) -> pd.DataFrame:
    """Get relevant pypi metadata for a list of packages.

    Args:
        packages: A list of Package objects (each having `.name` and `.version` attributes)
        urls: A series of URLs indexed by package (name, version)

    Returns: A table of pypi features indexed by package (name, version)
    """
    constructor = GithubPackageConstructor(urls=urls)
    gh_pkgs = [constructor(package) for package in packages]
    df = download_github_data(gh_pkgs)
    return INDEX(df)
