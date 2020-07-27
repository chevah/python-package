Python Portable Package
=======================

Build system for a portable Python distribution.

Used by Chevah's Buildbot setup to generate and publish binary Python
packages for a variety of platforms.

Please check https://github.com/chevah/python-package/releases for
latest packages. For older releases or platforms no longer supported,
please check https://binary.chevah.com/production/python/.

Building steps as used by Buildbot:

* Login to a system running on the desired platform (e.g. Ubuntu Server 20.04).
* Get the code for this repository from GitHub.
* ``./brink.sh detect_os``
* ``./chevah_build build``
* ``./chevah_build test``
* ``./chevah_build test_compat``

You can try the above steps on your own to build and test a new Python package.

To have new Python packages uploaded (typically for all supported platforms),
you should try the following, after securing access to Chevah infrastructure:

* ``./brink.sh test_remote group-all --properties=force_upload_production=yes

Use ``./chevah_build help`` to discover all available commands.


Patching upstream code
----------------------

This repository contains a lot of imported code from upstream repos:
Python, OpenSSL, SQLite, gmp, libffi, PyCrypto, etc.

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

This Python package builds on and links to third-party libraries.

To document them for all OS'es and to list their known vulnerabilities,
the LibreOffice spreadsheet ``external_deps.fods`` is used.

For your convenience, this flat ODS file is also exported in CSV format in
``external_deps.csv``.
