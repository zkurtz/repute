"""Main entry point for the repute package."""

import textwrap
from pathlib import Path

import click
import pandas as pd

import repute
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


def _format_table(df: pd.DataFrame) -> str:
    return textwrap.indent(str(df), "    ")


def summarize(df: pd.DataFrame) -> None:
    """Generate a summary report."""
    n_deps = len(df)
    click.echo(f"\nSummarizing {n_deps} dependencies:")

    # Check for old packages:
    age_col = "pypi:version_age_days"
    old_deps = df[[age_col]].sort_values(age_col).tail(min(3, n_deps))  # pyright: ignore[reportCallIssue]
    click.echo("\nHere are your oldest dependencies:")
    click.echo(_format_table(old_deps))

    # Check for non-github packages
    gh_col = "gh:github_url"
    missing_gh = df[gh_col].isna()
    assert isinstance(missing_gh, pd.Series), "Expected a series"
    if missing_gh.any():
        click.echo("\nThe following packages could not be found on GitHub:")
        click.echo(_format_table(df.loc[missing_gh][[]].reset_index()[["name", "version"]]))

    # Check for low stargazer count:
    stars_col = "gh:stars"
    gdf = df.loc[~missing_gh]
    nonstellar_deps = gdf[[stars_col]].dropna().sort_values(stars_col).head(min(3, n_deps))
    nonstellar_deps[stars_col] = nonstellar_deps[stars_col].astype(int)
    click.echo("\nHere are your least popular dependencies in terms of GitHub stars:")
    click.echo(_format_table(nonstellar_deps))


@click.command()
@click.version_option(version=repute.__version__, prog_name="repute")
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
    summarize(df)

    df.to_csv(output)
    click.echo(f"\nSee {output} for detailed results.")


if __name__ == "__main__":
    main()
