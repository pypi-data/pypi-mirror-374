Introduction
============


.. image:: https://readthedocs.org/projects/state-of-things/badge/?version=latest
    :target: https://state-of-things.readthedocs.io/
    :alt: Documentation Status


.. image:: https://github.com/mindwidgets/state-of-things/workflows/Build%20CI/badge.svg
    :target: https://github.com/mindwidgets/state-of-things/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

State of Things is a python library to organize complex state machines.


Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the library locally `from
PyPI <https://pypi.org/project/state-of-things/>`_.
To install for current user:

.. code-block:: shell

    pip3 install state-of-things

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install state-of-things

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install state-of-things


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://state-of-things.readthedocs.io/>`_.

Development
===========

To set up a development environment, clone the repository and install the development dependencies:
.. code-block:: shell

    git clone https://github.com/mindwidgets/state-of-things.git
    cd state-of-things
    pip install -r requirements-dev.txt

Then you can run the build (including tests) with:
.. code-block:: shell

    tox
