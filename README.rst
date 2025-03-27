.. role:: bash(code)
  :language: bash

********
Shrinkix
********

|ci-docs| |ci-lint| |ci-tests| |pypi| |versions| |discord| |license|

.. |ci-docs| image:: https://github.com/Dashstrom/shrinkix/actions/workflows/docs.yml/badge.svg
  :target: https://github.com/Dashstrom/shrinkix/actions/workflows/docs.yml
  :alt: CI : Docs

.. |ci-lint| image:: https://github.com/Dashstrom/shrinkix/actions/workflows/lint.yml/badge.svg
  :target: https://github.com/Dashstrom/shrinkix/actions/workflows/lint.yml
  :alt: CI : Lint

.. |ci-tests| image:: https://github.com/Dashstrom/shrinkix/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/Dashstrom/shrinkix/actions/workflows/tests.yml
  :alt: CI : Tests

.. |pypi| image:: https://img.shields.io/pypi/v/shrinkix.svg
  :target: https://pypi.org/project/shrinkix
  :alt: PyPI : shrinkix

.. |versions| image:: https://img.shields.io/pypi/pyversions/shrinkix.svg
  :target: https://pypi.org/project/shrinkix
  :alt: Python : versions

.. |discord| image:: https://img.shields.io/badge/Discord-dashstrom-5865F2?style=flat&logo=discord&logoColor=white
  :target: https://dsc.gg/dashstrom
  :alt: Discord

.. |license| image:: https://img.shields.io/badge/license-MIT-green.svg
  :target: https://github.com/Dashstrom/shrinkix/blob/main/LICENSE
  :alt: License : MIT

Description
###########

Reduces the size of images for the web.

Documentation
#############

Documentation is available on https://dashstrom.github.io/shrinkix

Installation from scratch
#########################

Windows
*******

Open an Admin PowerShell with :bash:`windows + X`, then press :bash:`a`.

..  code-block:: powershell

  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

MacOs and Linux
***************

..  code-block:: bash

  curl -LsSf https://astral.sh/uv/install.sh | sh

Package installation (All System)
*********************************

You can install :bash:`shrinkix` using `uv <https://github.com/astral-sh/uv>`_
from `PyPI <https://pypi.org/project/shrinkix>`_

..  code-block:: bash

  uv tool install shrinkix

Usage
#####

Usage as script
***************

..  code-block:: bash

  shrinkix image.png --max-width 1024 --max-height 1024 --artist 'Dashstrom' --copyright 'dashstrom.pro@gmail.com'

Usage as module
***************

..  code-block:: python

  from shrinkix import Shrinkix

  shrinkix = Shrinkix(
      max_width=1024,
      max_height=1024,
      keep_metadata=False,
  )
  shrinkix.shrink("tests/resources/test.jpg", "test.png")

Development
###########

Contributing
************

Contributions are very welcome. Tests can be run with :bash:`poe check`, please
ensure the coverage at least stays the same before you submit a pull request.

Setup
*****

You need to install `uv <https://github.com/astral-sh/uv>`_
and `Git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_
for work with this project.

..  code-block:: bash

  git clone https://github.com/Dashstrom/shrinkix
  cd shrinkix
  uv sync
  uv run poe setup

Poe
********

Poe is available for help you to run tasks.

..  code-block:: text

  test           Run test suite.
  lint           Run linters: ruff checker and ruff formatter and mypy.
  format         Run linters in fix mode.
  check          Run all checks: lint, test and docs.
  check-tag      Check if the current tag match the version.
  cov            Run coverage for generate report and html.
  open-cov       Open html coverage report in webbrowser.
  docs           Build documentation.
  open-docs      Open documentation in webbrowser.
  setup          Setup pre-commit.
  pre-commit     Run pre-commit.
  commit         Test, commit and push.
  clean          Clean cache files.

Skip commit verification
************************

If the linting is not successful, you can't commit.
For forcing the commit you can use the next command :

..  code-block:: bash

  git commit --no-verify -m 'MESSAGE'

Commit with commitizen
**********************

To respect commit conventions, this repository uses
`Commitizen <https://github.com/commitizen-tools/commitizen?tab=readme-ov-file>`_.

..  code-block:: bash

  cz c

How to add dependency
*********************

..  code-block:: bash

  uv add 'PACKAGE'

Ignore illegitimate warnings
****************************

To ignore illegitimate warnings you can add :

- **# noqa: ERROR_CODE** on the same line for ruff.
- **# type: ignore[ERROR_CODE]** on the same line for mypy.
- **# pragma: no cover** on the same line to ignore line for coverage.
- **# doctest: +SKIP** on the same line for doctest.

Uninstall
#########

..  code-block:: bash

  pipx uninstall shrinkix

License
#######

This work is licensed under `MIT <https://github.com/Dashstrom/shrinkix/blob/main/LICENSE>`_.
