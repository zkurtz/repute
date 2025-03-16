# reputation

Python package dependency analytics. Know what you depend on!

**This is a pre-alpha release. The package is available on pypi only to reserve the name space.**

`reputation` takes your `requirements.txt` and scans data sources on the web to output a columnar report of metrics that help you understand the health of your dependencies.

## Quickstart guide

The first step is to generate a `requirements.txt` file for your project. For illustration, we'll use the `demo` directory in this repo:
```
cd demo
# create a virtual environment and activate it:
# uv sync
# source .venv/bin/activate
pip freeze --exclude-editable > requirements.txt
```

Next, do `pip install reputation`  (or do `pip install .` in your clone of the repo) and run `reputation requirements.txt`. This will output a csv file with a report on the health of your dependencies:

Finally, upload your `reputation_report.csv` to a spreadsheet application and sort it on the various metrics columns to get a sense of the health of your dependencies. We've uploaded our demo example to a public spreadsheet on Google Sheets [here]() (coming soon ...). Consider following sorting that spreadsheet on each column as you read about each metric below.

## Overview of reputation metrics

First, hopefully it goes without saying none of these metrics in isolation are highly informative; defining and measuring reputation is a complex problem, so each of these metrics should be considered only starting point.

### Version age

If the version of a package you depend on is very old, this may increase the risk that your package includes bugs that have been fixed in newer versions or simply be less efficient or powerful than state-of-the-art packages.

### Time since latest package release

If a package has not been updated in a long time, this may indicate that the package is no longer maintained, which could be a problem if you encounter a bug or need a new feature.

### PyPI download count

Coming soon ...

### Github star count

Coming soon ...

## Details

Installation:
- We're [on pypi](https://pypi.org/project/reputation/), so `pip install reputation`.
- Consider using the [simplest-possible virtual environment](https://gist.github.com/zkurtz/4c61572b03e667a7596a607706463543) if working directly on this repo.
