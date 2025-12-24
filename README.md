# repute

Are your python project dependencies of good repute? Now you can run `repute` to describe the health of your dependencies based on data sources from the web.

## Quickstart guide

1. Generate a `requirements.txt` file for your project.
1. Install repute: `uv add repute`, ideally in its own virtual environment, so that it does not become part of the project that you want to analyze.
1. Run `repute path/to/requirements.txt` to analyze the health of your dependencies:

```
$ repute demo/requirements.txt
/Users/me/Desktop/mycloud/repos/repute/repute/requirements.py:31: UserWarning: ignoring editable installation: '-e file:///my/repo/path'
  warnings.warn(f"ignoring editable installation: '{line}'")
Fetching data from PyPI: 100%|███████████████████████████████████████████████████████████████████████████████████████| 112/112
Fetching download stats from PyPI: 100%|██████████████████████████████████████████████████████████████████████████████| 56/56
Fetching data from GitHub: 100%|███████████████████████████████████████████████████████████████████████████████████████| 54/54

Summarizing 56 dependencies:

Oldest dependencies:
                                  pypi:version_age_days  pypi:time_since_last_release_days
    name                 version
    jsonpatch            1.33                       642                                642
    azure-datalake-store 0.0.53                     679                                679
    mpmath               1.3.0                      744                                744

Dependencies that we could not locate on GitHub:
    ruamel-yaml
    ruamel-yaml-clib

Dependencies with fewest GitHub stars:
                               gh:stars
    name
    astropy-iers-data                 3
    jsonschema-specifications        11
    propcache                        17

Dependencies with fewest recent downloads:
                       pypi:recent_avg_downloads_per_day
    name
    astropy-iers-data                            2274182
    pyerfa                                       6626394
    astropy                                      7289296

See repute.csv for detailed results.
```

## Installation

Installation:
- We're [on pypi](https://pypi.org/project/repute/), so `pip install repute`.
- Consider using the [simplest-possible virtual environment](https://gist.github.com/zkurtz/4c61572b03e667a7596a607706463543) if working directly on this repo.

## Context and discussion

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
