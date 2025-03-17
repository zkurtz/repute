# repute

Python package dependency analytics. Know what you depend on!

**This is a pre-alpha release. The package is available on pypi only to reserve the name space.**

`repute` takes your `requirements.txt` and scans data sources on the web to output a columnar report of metrics that help you understand the health of your dependencies.

## Quickstart guide

The first step is to generate a `requirements.txt` file for your project. For illustration, we'll use the `demo` directory in this repo:
```
cd demo
# create a virtual environment and activate it:
# uv sync
# source .venv/bin/activate
pip freeze --exclude-editable > requirements.txt
```

Next, install repute like `pip install repute`, ideally in its own virtual environment, so that it does not become part of the project that you want to analyze.

Run `repute requirements.txt` to output a `repute_report.csv` file with a report on the health of your dependencies. Upload this to a spreadsheet application and sort it on the various metrics columns to get a sense of the health of your dependencies. We've uploaded our demo example to a public spreadsheet on Google Sheets [here]() (coming soon ...).

## Overview of `repute` metrics

First, hopefully it goes without saying none of these metrics in isolation are highly informative; defining and measuring repute is a complex problem, so each of these metrics should be considered only starting point.

### `version_age_days`

If the version of a package you depend on is very old, this may increase the risk that your package includes bugs that have been fixed in newer versions or simply be less efficient or powerful than state-of-the-art packages.

### `time_since_latest_release_days`

If a package has not been updated in a long time, this may indicate that the package is no longer maintained, which could be a problem if you encounter a bug or need a new feature.

### `download_count`

Coming soon ...

### `star_count`

Coming soon ...

## Installation

Installation:
- We're [on pypi](https://pypi.org/project/repute/), so `pip install repute`.
- Consider using the [simplest-possible virtual environment](https://gist.github.com/zkurtz/4c61572b03e667a7596a607706463543) if working directly on this repo.


## Background

Assessing the quality of python dependencies is a complex problem that goes far beyond the scope of this package. Here's a brief overview of the types of factors that could be considered in a more comprehensive review:

1. **Dependency health metrics:**
   - Total dependency count (direct and transitive)
   - Dependency tree depth
   - Presence of known problematic dependencies
   - Supply chain integrity (signed packages, integrity verification)

1. **Maintenance indicators:**
   - Time since last commit/release
   - Release frequency and consistency
   - Issue resolution time
   - Pull request responsiveness
   - Number of active maintainers
   - Bus factor (concentration of commits among maintainers)

1. **Code quality metrics:**
   - Test coverage percentage
   - CI/CD pipeline robustness
   - Static analysis scores
   - Documentation completeness
   - Adherence to PEP standards
   - Type hint coverage
   - Presence of deprecation warnings

1. **Community health:**
   - GitHub stars/forks trend over time
   - Download statistics from PyPI
   - Stack Overflow question frequency and answer rates
   - Corporate backing or foundation support

1. **Operational considerations:**
   - Package size (both download and installed)
   - Import time impact
   - Memory footprint
   - Performance benchmarks
   - Compatibility with target Python versions
   - Platform compatibility (Windows/Linux/macOS)

1. **Security-specific indicators:**
   - OSSF Scorecard results
   - Use of memory-unsafe dependencies (C extensions)
   - History of CVEs and their severity
   - Time to patch previous vulnerabilities
   - Application of secure coding practices
   - Two-factor authentication usage by maintainers
   - Dependency pinning practices

1. **Build process integrity:**
   - Reproducible builds support
   - Build artifact signing
   - Provenance information availability
   - Software Bill of Materials (SBOM) availability

1. **API stability:**
   - Breaking change frequency
   - Deprecation policy adherence
   - Semantic versioning compliance
