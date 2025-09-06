# core-mixins
===============================================================================

This project contains common functions, decorators, and mixin classes 
as the base for other projects or libraries...

===============================================================================

.. image:: https://img.shields.io/pypi/pyversions/core-mixins.svg
    :target: https://pypi.org/project/core-mixins/
    :alt: Python Versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-mixins/-/blob/main/LICENSE
    :alt: License

.. image:: https://gitlab.com/bytecode-solutions/core/core-mixins/badges/release/pipeline.svg
    :target: https://gitlab.com/bytecode-solutions/core/core-mixins/-/pipelines
    :alt: Pipeline Status

.. image:: https://readthedocs.org/projects/core-mixins/badge/?version=latest
    :target: https://readthedocs.org/projects/core-mixins/
    :alt: Docs Status

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security

|

Execution Environment
---------------------------------------

Install libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install --upgrade pip 
    pip install virtualenv
..

Create the Python Virtual Environment.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    virtualenv --python={{python-version}} .venv
    virtualenv --python=python3.11 .venv
..

Activate the Virtual Environment.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    source .venv/bin/activate
..

Install required libraries.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    pip install .
..

Check tests and coverage.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    python manager.py run-tests
    python manager.py run-coverage
..
