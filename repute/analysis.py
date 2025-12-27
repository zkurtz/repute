"""Main entry point for the repute package."""

import textwrap

import click
import pandas as pd
from sigfig import round as sround

from repute import data

MAX_NUM_PACKAGES_DISPLAY = 10


def _soft_sigfig_fmt(num: float | int, sigfigs=2) -> str:
    """Format a number with a given number of significant figures.

    Any rounding applies only to decimal digits, not to the number of digits in the integer part.
    """
    num_str = str(num)
    num_nondecimal_digits = len(num_str.split(".")[0])
    ndigits = max(sigfigs, num_nondecimal_digits)
    return sround(num_str, sigfigs=ndigits, spacer=",")


def _format_table(df: pd.DataFrame) -> str:
    # format numeric columns with 2 significant figures
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        df[col] = [_soft_sigfig_fmt(item) for item in df[col]]
    return textwrap.indent(str(df), "    ")


def _format_list(series: pd.Series) -> str:
    return textwrap.indent("\n".join(series), "    ")


def summarize(df: pd.DataFrame, max_old_deps: int = MAX_NUM_PACKAGES_DISPLAY) -> None:
    """Generate a summary report."""
    n_deps = len(df)
    click.echo(f"\nSummarizing {n_deps} dependencies:")

    # Check for old packages:
    age_col = "pypi:version_age_days"
    cols = [
        age_col,
        "pypi:time_since_last_release_days",
    ]
    old_deps = df[cols].sort_values(age_col).tail(min(max_old_deps, n_deps))  # pyright: ignore[reportCallIssue]
    # reverse the order to have oldest first
    old_deps = old_deps.iloc[::-1]
    click.echo("\nOldest dependencies:")
    click.echo(_format_table(old_deps))

    # Check for non-github packages
    gh_col = "gh:github_url"
    missing_gh = df[gh_col].isna()
    assert isinstance(missing_gh, pd.Series), "Expected a series"
    if missing_gh.any():
        click.echo("\nDependencies that we could not locate on GitHub:")
        click.echo(_format_list(df.loc[missing_gh][[]].reset_index()["name"]))

    # Check for low stargazer count:
    stars_col = "gh:stars"
    gdf = data.NAME_INDEX(df.loc[~missing_gh])
    num_display = min(MAX_NUM_PACKAGES_DISPLAY, n_deps)
    nonstellar_deps = gdf[[stars_col]].dropna().sort_values(stars_col).head(num_display)  # pyright: ignore[reportCallIssue]
    nonstellar_deps[stars_col] = nonstellar_deps[stars_col].astype(int)
    click.echo("\nDependencies with fewest GitHub stars:")
    click.echo(_format_table(nonstellar_deps))

    # Check for rarely-downloaded packages:
    downloads_col = "pypi:recent_avg_downloads_per_day"
    low_downloads = data.NAME_INDEX(df)[[downloads_col]].sort_values(downloads_col).head(num_display)  # pyright: ignore[reportCallIssue]
    click.echo("\nDependencies with fewest recent downloads:")
    click.echo(_format_table(low_downloads))
