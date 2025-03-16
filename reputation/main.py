"""Main entry point for the reputation package."""

from pathlib import Path

import click

from reputation import requirements
from reputation.pypi import analytics as pypi_analytics

DEFAULT_OUTPUT_PATH = "reputation_report.csv"


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--output", type=click.Path(), default=DEFAULT_OUTPUT_PATH)
def main(input: str, *, output: str = DEFAULT_OUTPUT_PATH) -> None:
    """Analyze PyPI metadata from a requirements file."""
    packages = requirements.parse(Path(input))
    pypi_df = pypi_analytics.get_features(packages)
    pypi_df.to_csv(output)
    click.echo(f"Saved results to {output}")


if __name__ == "__main__":
    main()
