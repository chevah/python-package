Python Portable Package
=======================

.. image:: https://github.com/chevah/python-package/workflows/Bare/badge.svg
  :target: https://github.com/chevah/python-package/actions/workflows/bare.yaml

.. image:: https://github.com/chevah/python-package/workflows/Docker/badge.svg
  :target: https://github.com/chevah/python-package/actions/workflows/docker.yaml

Build system for a portable Python distribution.

Used by Chevah's Buildbot setup to generate and publish binary Python
packages for a variety of platforms.

Please check https://github.com/chevah/python-package/releases for
latest packages. For older releases or platforms no longer supported,
please check https://binary.chevah.com/production/python/.

Building steps:

* Login to a system running on the desired platform (e.g. Ubuntu Server 20.04).
* Get the code for this repository from GitHub.
* ``./brink.sh detect_os``
* ``./chevah_build build``
* ``./chevah_build test``
* ``./chevah_build compat``

You can try the above steps on your own to build and test a new Python package.

Use ``./chevah_build help`` to discover all available commands.

New testing packages are uploaded automatically for green GitHub builds at
https://bin.chevah.com:20443/testing/.

Production packages are available both through GitHub releases and at
https://bin.chevah.com:20443/production/.


Patching upstream code
----------------------

This repository contains a lot of imported code from upstream repos:
Python, OpenSSL, SQLite, libffi, etc.

You can find those sources in two sub-directories:

* ``src/``
* ``python-modules/``

Local changes to upstream projects are kept separated from upstream code.
For every problem we fix downstream, there's a patch to be applied at build
time. Those patches are kept in one of these places:

* ``src/$PROJECT/*.patch``
* ``python-modules/$PROJECT-$VERSION-patches/``

New patches added as documented above will be picked up automatically
by the build system.

An example for creating a patch for src/python/Python-2.7.13/Lib/site.py::

    cd src/python/Python-2.7.13/
    cp Lib/site.py Lib/site-patched.py
    # Edit Lib/site-patched.py as needed, then create the diff.
    diff -ur Lib/site.py Lib/site-patched.py
    # Save the diff result, including the command line into a patch file,
    # for example:
    src/python/this-fixes-something.patch


External dependencies and associated vulnerabilities
----------------------------------------------------

This Python package builds and/or links to third-party libraries.

Their known vulnerabilities are documented for all OS'es in the
LibreOffice spreadsheet ``external_deps.fods``.

For your convenience, this flat ODS file is also exported in CSV format as
``external_deps.csv``.
