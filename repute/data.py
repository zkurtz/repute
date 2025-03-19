"""Core data structures for python package metadata."""

from attrs import asdict, frozen
from pandahandler.indexes import Index

INDEX = Index(
    names=[
        "name",
        "version",
    ]
)
NAME_INDEX = Index(names=["name"], require_unique=False)


@frozen
class Package:
    """Metadata for a package."""

    name: str
    version: str

    def __str__(self) -> str:
        """String representation of the package and version."""
        return f"{self.name}__{self.version}"

    @property
    def dict(self) -> dict[str, str]:
        """Dictionary representation of the package."""
        return asdict(self)


# Known github repo URLs index by package name
KNOWN_GITHUB_REPOS = {
    "adlfs": "github.com/fsspec/adlfs",
    "msal-extensions": "github.com/AzureAD/microsoft-authentication-extensions-for-python",
}
