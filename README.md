# reputation

Python package dependency analytics. Know what you depend on!

**This is a pre-alpha release. The package is available on pypi only to reserve the name space.**

`reputation` takes your `requirements.txt` and scans data sources on the web to output a columnar report of metrics that help you understand the health of your dependencies.

## Quick start guide

This guide assumes that you use a uv-based python virtual environment:
```
# generate current pinned requirements:
uv pip freeze --exclude-editable > requirements.txt

# install reputation and use it to generate a report:
uv pip install reputation
reputation requirements.txt > reputation_report.csv
```

Upload your csv to a spreadsheet application and sort it on the various metrics columns to get a sense of the health of your dependencies.


## Details

Installation:
- We're [on pypi](https://pypi.org/project/reputation/), so `pip install reputation`.
- Consider using the [simplest-possible virtual environment](https://gist.github.com/zkurtz/4c61572b03e667a7596a607706463543) if working directly on this repo.
