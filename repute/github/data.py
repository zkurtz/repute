"""Data structures for GitHub package metadata."""

from attrs import frozen

from repute.data import Package


@frozen
class GithubPackage(Package):
    """Metadata for a package on GitHub."""

    github_url: str
    repo_owner: str
    repo_name: str
