"""Main entry point for the repute package."""

from pathlib import Path

import click
import pandas as pd

import repute
from repute import data, requirements
from repute.analysis import summarize
from repute.github import analytics as gh_analytics
from repute.pypi import analytics as pypi_analytics

DEFAULT_OUTPUT_PATH = "repute.csv"
GITHUB_URL = "github_url"

PYPI_REPORT_COLS = [
    "version_age_days",
    "time_since_last_release_days",
]
GH_REPORT_COLS = [
    "stars",
    "watchers",
    GITHUB_URL,
]


def load_pypi_data(packages: list[data.Package]) -> pd.DataFrame:
    """Load PyPI data for a list of packages."""
    df_detailed = pypi_analytics.get_features(packages)
    df = df_detailed[PYPI_REPORT_COLS + [GITHUB_URL]].copy()
    df.columns = [f"pypi:{col}" for col in df.columns]
    assert isinstance(df, pd.DataFrame), "Expected a data frame"
    return df


def adjust_github_urls(from_pypi: pd.Series) -> pd.DataFrame:
    """Corrections to github urls inferred from PyPI."""
    df = from_pypi.to_frame()
    df = data.NAME_INDEX(df)
    df = df.rename(columns={f"pypi:{GITHUB_URL}": GITHUB_URL})
    known_repos_series = pd.Series(data.KNOWN_GITHUB_REPOS)
    df.loc[known_repos_series.index, GITHUB_URL] = known_repos_series
    return data.INDEX(df)


def load_github_data(df: pd.DataFrame) -> pd.DataFrame:
    """Load GitHub data for packages that we've managed to infer a github url."""
    gh_urls = df["github_url"].dropna()
    assert isinstance(gh_urls, pd.Series), "Expected a series"
    gh_df = gh_analytics.get_features(urls=gh_urls)
    gh_df = gh_df[GH_REPORT_COLS]
    gh_df.columns = [f"gh:{col}" for col in gh_df.columns]
    assert isinstance(gh_df, pd.DataFrame), "Expected a data frame"
    return gh_df


@click.command()
@click.version_option(version=repute.__version__, prog_name="repute")
@click.argument("input", type=click.Path(exists=True))
@click.option("--output", type=click.Path(), default=DEFAULT_OUTPUT_PATH)
def main(input: str, *, output: str = DEFAULT_OUTPUT_PATH) -> None:
    """Analyze PyPI metadata from a requirements file."""
    packages = requirements.parse(Path(input))
    df = load_pypi_data(packages)
    df["github_url"] = adjust_github_urls(df.pop("pypi:github_url"))
    gh_df = load_github_data(df)
    df = df.merge(gh_df, left_index=True, right_index=True, how="left")
    summarize(df)
    df.to_csv(output)
    click.echo(f"\nSee {output} for detailed results.")


if __name__ == "__main__":
    main()
