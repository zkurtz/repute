"""Data structures for GitHub package metadata."""

import pandas as pd
from attrs import frozen

from repute.data import Package


@frozen
class GithubPackage(Package):
    """Metadata for a package on GitHub."""

    url: str
    repo_owner: str
    repo_name: str


@frozen
class GithubPackageConstructor:
    """Construct a github package from a base package plus URL info."""

    urls: pd.Series

    def __call__(self, package: Package) -> GithubPackage:
        """Construct a github package from a base package plus URL info."""
        url = self.urls.loc[(package.name, package.version)]
        _, body = url.split("github.com/")
        parts = body.split("/")
        repo_owner = parts[0]
        repo_name = parts[1]
        return GithubPackage(
            url=url,
            repo_owner=repo_owner,
            repo_name=repo_name,
            **package.dict,
        )
