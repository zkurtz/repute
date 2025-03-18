"""Main entry point for the repute package."""

from pathlib import Path

import click
import pandas as pd
from pandahandler.frames.joiners import safe_hstack

from repute import requirements
from repute.github import analytics as gh_analytics
from repute.pypi import analytics as pypi_analytics

DEFAULT_OUTPUT_PATH = "repute_report.csv"

PYPI_REPORT_COLS = [
    "version_age_days",
    "time_since_last_release_days",
]
GH_REPORT_COLS = [
    "stars",
    "watchers",
    "github_url",
]


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--output", type=click.Path(), default=DEFAULT_OUTPUT_PATH)
def main(input: str, *, output: str = DEFAULT_OUTPUT_PATH) -> None:
    """Analyze PyPI metadata from a requirements file."""
    packages = requirements.parse(Path(input))

    # Get data from pypi:
    pypi_df_detailed = pypi_analytics.get_features(packages)
    pypi_df = pypi_df_detailed[PYPI_REPORT_COLS].copy()
    pypi_df.columns = [f"pypi:{col}" for col in pypi_df.columns]
    assert isinstance(pypi_df, pd.DataFrame), "Expected a data frame"

    # Get more data from github:
    gh_urls = pypi_df_detailed["github_url"]
    assert isinstance(gh_urls, pd.Series), "Expected a series"
    gh_df = gh_analytics.get_features(packages, urls=gh_urls)
    gh_df = gh_df[GH_REPORT_COLS]
    gh_df.columns = [f"gh:{col}" for col in gh_df.columns]
    assert isinstance(gh_df, pd.DataFrame), "Expected a data frame"

    df = safe_hstack([pypi_df, gh_df])
    df.to_csv(output)
    click.echo(f"Saved results to {output}")


if __name__ == "__main__":
    main()
