# Shrinkix

[![CI : Docs](https://github.com/Dashstrom/shrinkix/actions/workflows/docs.yml/badge.svg)](https://github.com/Dashstrom/shrinkix/actions/workflows/docs.yml) [![CI : Lint](https://github.com/Dashstrom/shrinkix/actions/workflows/lint.yml/badge.svg)](https://github.com/Dashstrom/shrinkix/actions/workflows/lint.yml) [![CI : Tests](https://github.com/Dashstrom/shrinkix/actions/workflows/tests.yml/badge.svg)](https://github.com/Dashstrom/shrinkix/actions/workflows/tests.yml) [![PyPI : shrinkix](https://img.shields.io/pypi/v/shrinkix.svg)](https://pypi.org/project/shrinkix) [![Python : versions](https://img.shields.io/pypi/pyversions/shrinkix.svg)](https://pypi.org/project/shrinkix) [![License : MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/Dashstrom/shrinkix/blob/main/LICENSE)

Reduces the size of images for the web.

## Documentation

Documentation is available on <https://dashstrom.github.io/shrinkix>.

## Installation

```bash
# Using pip
pip install shrinkix
# Using uv (install in your project dependencies)
uv add shrinkix
# Using pipx (install as a tool in a venv)
pipx install shrinkix
# Using uv (install as a tool in a venv)
uv tool install shrinkix
```

## Usage

### Usage as CLI

```bash
shrinkix image.png --max-width 1024 --max-height 1024 --artist 'You' --copyright 'you@example.com'
```

### Usage as module

```python
from shrinkix import Shrinkix

shrinkix = Shrinkix(
    max_width=1024,
    max_height=1024,
    keep_metadata=False,
)
shrinkix.shrink("tests/resources/test.jpg", "test.png")
```

## Development

### Contributing

Contributions are very welcome. Tests can be run with `poe check`, please ensure the coverage at least stays the same before you submit a pull request.

### Prerequisite

First, You need to install [git](https://git-scm.com) following [the official guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and configure it.

Then, you need to install [uv](https://docs.astral.sh/uv/getting-started/installation) and update shell path with this command:

```bash
uv tool update-shell
```

Finally, run these commands for setup the project with dev dependencies.

```bash
git clone https://github.com/Dashstrom/shrinkix
cd shrinkix
uv sync --all-extras --python 3.10
uv run poe setup
```

### Poe

Poe is available for help you to run tasks: `uv run poe {task}` or `poe task` within the venv.

```text
test                  Run test suite.
lint                  Run linters: ruff checker and ruff formatter and mypy.
format                Run linters in fix mode.
check                 Run all checks: lint, test and docs.
check-tag             Check if the current tag match the version.
cov                   Run coverage for generate report and html.
open-cov              Open html coverage report in webbrowser.
doc                   Build documentation.
open-doc              Open documentation in webbrowser.
setup                 Setup pre-commit.
pre-commit            Run pre-commit.
clean                 Clean cache files.
```

### How to add dependency

```bash
uv add 'PACKAGE'
```

### Ignore illegitimate warnings

To ignore illegitimate warnings you can add :

- **# noqa: ERROR_CODE** on the same line for ruff.
- **# type: ignore[ERROR_CODE]** on the same line for mypy.
- **# pragma: no cover** on the same line to ignore line for coverage.
- **# doctest: +SKIP** on the same line for doctest.

## License

This work is licensed under [MIT](https://github.com/Dashstrom/shrinkix/blob/main/LICENSE).
