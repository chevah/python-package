# Copyright (c) 2010-2013 Adi Roiban.
# See LICENSE for details.
"""
Build script for Python binary distribution.
"""
from __future__ import with_statement
import sys

# Marker for paver.sh.
# This value is pavers by bash. Use a strict format.
BRINK_VERSION = '0.8.1'

EXTRA_PACKAGES = []

from brink.pavement_commons import (
    _p,
    buildbot_list,
    buildbot_try,
    default,
    harness,
    help,
    pave,
    SETUP,
    test_remote,
    )
from paver.easy import task

# Make pylint shut up.
buildbot_list
buildbot_try
default
harness
help
test_remote

SETUP['product']['name'] = 'python'
SETUP['folders']['source'] = u'src'
SETUP['repository']['name'] = u'python'
SETUP['pocket-lint']['include_files'] = ['pavement.py']
SETUP['pocket-lint']['include_folders'] = ['src']
SETUP['pocket-lint']['exclude_files'] = []
SETUP['test']['package'] = None


@task
def deps():
    """
    Copy external dependencies.
    """
    print('Installing dependencies to %s...' % (pave.path.build))
    pave.installRunDependencies(extra_packages=EXTRA_PACKAGES)
    pave.installBuildDependencies()
