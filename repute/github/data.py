"""Data structures for GitHub package metadata."""

from attrs import frozen

from repute.data import Package


@frozen
class GithubPackage(Package):
    """Metadata for a package on GitHub."""

    url: str
    repo_owner: str | None
    repo_name: str | None
