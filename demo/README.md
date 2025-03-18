# Demo project for `repute`

This project exists only to demonstrate the creation and usage of list of package requirements to be analyzed by the `repute` tool. See the top-level README.md for example usage.

## Dev notes

Simply running `uv sync` will get confused with the package information in the parent directory.. Instead, create the demo virtual env in this directory as

```
uv venv
source .venv/bin/activate
uv sync --active
```

Generate the requirement.txt file with `uv pip freeze --exclude-editable > requirements.txt`.
