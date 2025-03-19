# Demo project for `repute`

This project exists to create an example input `requirements.txt` to demo the usage of the `repute` tool.

Simply running `uv sync` will get confused with the package information in the parent directory. Instead, create the demo virtual env in this directory as

```
# sim
uv venv
source .venv/bin/activate
uv sync --active
```

Generate the requirement.txt file with `uv pip freeze > requirements.txt`.

Copy-paste this to the end of `requirements.txt`:
```
# `repute` will ignore any editable installations
-e file:///my/repo/path
```
