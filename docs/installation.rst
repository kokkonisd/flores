Installation
************

.. note::

    Flores is available under Python 3.9 or greater on Ubuntu and macOS.

To install Flores, you'll need an up-to-date Python and `pip`.


Install via PyPI (recommended)
==============================

To install Flores via `PyPI <https://pypi.org/>`_, run the following command:

.. code-block:: console

    $ pip install flores


Install from source
===================

To install Flores from source, you'll need to clone its repo first. There are two active
branches:

* ``main``: the main, *stable* branch, that contains the latest stable changes that have
  not made their way into a release yet.
* ``dev``: the development, *unstable* branch, that contains possibly unstable changes.

For example, to clone the ``main`` branch (which is also the default branch), you can
run:

.. code-block:: console

   $ git clone git@github.com:kokkonisd/flores.git


Once you have the sources, you can run (inside the sources directory):

.. code-block:: console

   $ pip install .


Verifying the installation
==========================

To make sure that Flores is properly installed, you can run:

.. code-block:: console

   $ flores --version

This should print the version of the currently installed Flores.
