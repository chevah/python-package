# Copyright (c) 2010-2013 Adi Roiban.
# See LICENSE for details.
"""
Build script for Python binary distribution.
"""

RUN_PACKAGES = [
    'zope.interface==3.8.0',
    'twisted==12.1.0-chevah3',

    # Buildbot is used for try scheduler
    'buildbot==0.8.8.c1',

    # Required for some unicode handling.
    'unidecode',
    ]

from brink.pavement_commons import (
    buildbot_list,
    buildbot_try,
    default,
    github,
    harness,
    help,
    pave,
    SETUP,
    test_remote,
    test_review,
    )
from paver.easy import task

# Make pylint shut up.
buildbot_list
buildbot_try
default
github
harness
help
test_remote
test_review

SETUP['product']['name'] = 'python'
SETUP['folders']['source'] = u'src'
SETUP['repository']['name'] = u'python-package'
SETUP['pocket-lint']['include_files'] = ['pavement.py']
SETUP['pocket-lint']['include_folders'] = ['src']
SETUP['pocket-lint']['exclude_files'] = []
SETUP['test']['package'] = None

SETUP['pypi']['index_url'] = 'http://pypi.chevah.com:10042/simple'
SETUP['github']['repo'] = 'chevah/python-package'
SETUP['buildbot']['server'] = 'build.chevah.com'
SETUP['buildbot']['web_url'] = 'http://build.chevah.com:10088'


@task
def deps():
    """
    Copy external dependencies.
    """
    print('Installing dependencies to %s...' % (pave.path.build))
    pave.pip(
        command='install',
        arguments=RUN_PACKAGES,
        )
