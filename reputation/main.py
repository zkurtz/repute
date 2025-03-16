"""Main entry point for the reputation package."""

from pathlib import Path

import click
import pandas as pd
from pandahandler.frames.joiners import safe_hstack

from reputation import requirements
from reputation.pypi import analytics as pypi_analytics

DEFAULT_OUTPUT_PATH = "reputation_report.csv"

PYPI_REPORT_COLS = [
    "version_age_days",
    "time_since_last_release_days",
]


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--output", type=click.Path(), default=DEFAULT_OUTPUT_PATH)
def main(input: str, *, output: str = DEFAULT_OUTPUT_PATH) -> None:
    """Analyze PyPI metadata from a requirements file."""
    packages = requirements.parse(Path(input))

    # Get data from pypi:
    pypi_df = pypi_analytics.get_features(packages)[PYPI_REPORT_COLS]
    pypi_df.columns = [f"pypi:{col}" for col in pypi_df.columns]
    assert isinstance(pypi_df, pd.DataFrame), "Expected a data frame"

    # Get more data from github:
    # TODO

    df = safe_hstack([pypi_df])
    df.to_csv(output)
    click.echo(f"Saved results to {output}")


if __name__ == "__main__":
    main()
