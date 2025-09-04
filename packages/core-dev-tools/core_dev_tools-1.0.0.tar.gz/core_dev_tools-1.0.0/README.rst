core-dev-tools
=======================================
***************************************


.. image:: https://img.shields.io/pypi/pyversions/core-dev-tools.svg
    :target: https://pypi.org/project/core-dev-tools/
    :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-dev-tools/-/blob/main/LICENSE
    :alt: License

|
This library provides common tools used for development, allowing projects
to use them without needing to define them individually, providing a set of tools
across the code ecosystem...

Available Tools
=======================================

UV
---------------------------------------
An extremely fast Python package and project manager, written in Rust.

More information: https://docs.astral.sh/uv/

.. code-block:: python

    uv [OPTIONS] <COMMAND>
..


Ruff Linter
---------------------------------------
The Ruff Linter is an extremely fast Python linter designed as 
a drop-in replacement for Flake8 (plus dozens of plugins), isort, 
pydocstyle, pyupgrade, autoflake, and more.

More information: https://docs.astral.sh/ruff/linter/

.. code-block:: python

    ruff check                  # Lint files in the current directory.
    ruff check --fix            # Lint files in the current directory and fix any fixable errors.
    ruff check --watch          # Lint files in the current directory and re-lint on change.
    ruff check path/to/code/    # Lint files in `path/to/code`.
..


PyLint
---------------------------------------
Pylint is a tool that checks for errors in Python code, tries to 
enforce a coding standard (stricter/static code analyzer (if you want more 
opinions than ruff)) and looks for bad code smells.

More information: https://docs.pylint.org/

.. code-block:: python

    pylint <module_or_package>
..


Mypy
---------------------------------------
Mypy is an optional static type checker for Python that aims to combine 
the benefits of dynamic (or "duck") typing and static typing.

More information:
  * https://mypy-lang.org/
  * https://mypy.readthedocs.io/en/stable/

.. code-block:: python

    mypy .
..


Pyright
---------------------------------------
Pyright is a full-featured, standards-compliant static type 
checker for Python. It is designed for high performance 
and can be used with large Python source bases.

More information: https://microsoft.github.io/pyright

.. code-block:: python

    pyright
..


Bandit
---------------------------------------
Bandit is a tool designed to find common security issues in Python 
code. To do this Bandit processes each file, builds an AST from 
it, and runs appropriate plugins against the AST nodes. Once Bandit 
has finished scanning all the files it generates a report.

More information: https://pypi.org/project/bandit/

.. code-block:: python

    bandit -r <path>
..


pip-audit
---------------------------------------
It is a tool for scanning Python environments for packages with known 
vulnerabilities. It uses the Python Packaging Advisory Database (https://github.com/pypa/advisory-database) 
via the PyPI JSON API as a source of vulnerability reports.

More information: https://pypi.org/project/pip-audit/

.. code-block:: python

    pip-audit
..


Tox
---------------------------------------
It aims to automate and standardize testing in Python. It is part of a 
larger vision of easing the packaging, testing and release process 
of Python software (alongside pytest and devpi).

More information:
  * https://pypi.org/project/tox/
  * https://tox.wiki


### taskipy
The complementary task runner for python.

More information: https://pypi.org/project/taskipy/

.. code-block:: python

    task <task-name>
..


Sphinx
---------------------------------------
Sphinx makes it easy to create intelligent and beautiful documentation.

More information: https://www.sphinx-doc.org/

.. code-block:: python

    sphinx-quickstart docs
    cd docs
    make html
..
