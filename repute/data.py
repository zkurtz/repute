"""Core data structures for python package metadata."""

from attrs import asdict, frozen
from pandahandler.indexes import Index

INDEX = Index(
    names=[
        "name",
        "version",
    ]
)


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
