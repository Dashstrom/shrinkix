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

Windows (Chocolatey, Python, Visual Studio Build Tools, pipx)
*************************************************************

Open an Admin PowerShell with :bash:`windows + R`, write :bash:`powershell` then press :bash:`ctrl + shift + enter`.

..  code-block:: powershell

  Set-ExecutionPolicy Bypass -Scope Process -Force
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  choco install python --version=3.10.11 --override --install-arguments '/quiet PrependPath=1 Include_debug=1 Include_symbols=1 SimpleInstall=1' -y
  choco install visualstudio2022-workload-vctools -y
  pip install --upgrade wheel pip pipx
  pipx ensurepath

Ubuntu (build requirement and pipx)
***********************************

..  code-block:: bash

  sudo apt -y update && sudo apt -y upgrade && sudo apt -y install python3-all-dev
  pip install --upgrade wheel pip pipx
  pipx ensurepath

Mac (Homebrew and pipx)
***********************

..  code-block:: bash

  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  echo "export PATH=/opt/homebrew/bin:$PATH" >> ~/.bash_profile && source ~/.bash_profile
  brew install python
  pip install --upgrade wheel pip pipx
  pipx ensurepath


Package installation
********************

You can install :bash:`shrinkix` using `pipx <https://pipx.pypa.io/stable/>`_
from `PyPI <https://pypi.org/project>`_

..  code-block:: bash

  pipx install shrinkix

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

You need to install `Poetry <https://python-poetry.org/docs/#installation>`_
and `Git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_
for work with this project.

..  code-block:: bash

  git clone https://github.com/Dashstrom/shrinkix
  cd shrinkix
  poetry install --all-extras
  poetry run poe setup
  poetry shell

Poe
********

Poe is available for help you to run tasks.

..  code-block:: text

  test           Run test suite.
  lint           Run linters: ruff linter, ruff formatter and mypy.
  format         Run linters in fix mode.
  check          Run all checks: lint, test and docs.
  cov            Run coverage for generate report and html.
  open-cov       Open html coverage report in webbrowser.
  docs           Build documentation.
  open-docs      Open documentation in webbrowser.
  setup          Setup pre-commit.
  pre-commit     Run pre-commit.
  clean          Clean cache files

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

  poetry add 'PACKAGE'

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
