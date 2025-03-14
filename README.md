# reputation

Python package dependency analytics. Know what you depend on!

**This is a pre-alpha release. The package is available on pypi only to reserve the name space.**

`reputation` takes your `requirements.txt` and scans data sources on the web to output a columnar report of metrics that help you understand the health of your dependencies.

## Quick start guide

This guide assumes that you use a uv-based python virtual environment.

Do `uv pip freeze > requirements.txt` to generate a `requirements.txt` file.

Then run `reputation` on the `requirements.txt` file:

```bash
pip install reputation
reputation requirements.txt > reputation_report.csv
```
