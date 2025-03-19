"""Main entry point for the repute package."""

from pathlib import Path

import click
import pandas as pd

from repute import requirements
from repute.github import analytics as gh_analytics
from repute.pypi import analytics as pypi_analytics

DEFAULT_OUTPUT_PATH = "repute.csv"

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

    # Get more data from github, for packages that have a github URL listed on PyPI:
    gh_urls = pypi_df_detailed["github_url"].dropna()
    assert isinstance(gh_urls, pd.Series), "Expected a series"
    gh_df = gh_analytics.get_features(urls=gh_urls)
    gh_df = gh_df[GH_REPORT_COLS]
    gh_df.columns = [f"gh:{col}" for col in gh_df.columns]
    assert isinstance(gh_df, pd.DataFrame), "Expected a data frame"

    df = pypi_df.merge(gh_df, left_index=True, right_index=True, how="left")
    df.to_csv(output)
    click.echo(f"Saved results to {output}")


if __name__ == "__main__":
    main()
