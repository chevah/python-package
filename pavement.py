# Copyright (c) 2010-2013 Adi Roiban.
# See LICENSE for details.
"""
Build script for Python binary distribution.
"""

# Marker for paver.sh.
# This value is pavers by bash. Use a strict format.
BRINK_VERSION = '0.31.1'
PYTHON_VERSION = '2.7'

RUN_PACKAGES = [
    'zope.component==4.1.0',
    'twisted==12.1.0-chevah3',
    # Required by twisted.conch
    'pyasn1',
    'lazr.delegates==1.2.0',
    # Required by documentation generation and as a generic template engine.
    'jinja2',
    'pygments',
    # We need to keep track of all dependencies here since, chevah.server
    # does not use setup.py for managing dependencies.
    'passlib',  # For generating hashed passwords.
    'sftpplus-website>=0.3.7',  # For generating documentation and download.
    'mysql-connector-python==1.0.12',
    'twistar==1.1-chevah4',
    'selenium==2.35.0',
    'python-dateutil==2.1',
    'bunch',
    # Our own libraries.
    'chevah-ftplib==2.7.3-chevah3',
    'chevah-compat==0.11.0',
    'chevah-empirical==0.17.5',
    'chevah-weblibs-angularjs==1.1.5-1',
    'chevah-weblibs-angular-ui-utils==43a71-chevah1',
    'chevah-weblibs-angular-ui-bootstrap==0.5.0-1',
    'chevah-weblibs-bootstrap==2.2.2-chevah2',
    'chevah-weblibs-sinon==1.5.2-chevah2',
    'chevah-weblibs-json3==3.2.4-chevah2',
    'chevah-weblibs-html5shiv==3.6.2pre-chevah2',
    'chevah-weblibs-moment==2.1.0-2',
    'chevah-weblibs-jquery==1.10.1-chevah2',
    'chevah-weblibs-select2==3.4.0-chevah2',
    'chevah-weblibs-angular-ui-select2==0-23e0ad-chevah1',
    'chevah-weblibs-ng-table==0-67f083-1',
    'chevah-weblibs-bootstrap-timepicker==0.2.3-chevah-3',
    'chevah-weblibs-bootstrap-datepicker==1.2.0-1',
    ]


BUILD_PACKAGES = [
    'zope.interface==3.8.0',

    # Buildbot is used for try scheduler
    'buildbot',

    # Required for some unicode handling.
    'unidecode',
    ]

from brink.pavement_commons import (
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
    pave.pip(
        command='install',
        arguments=BUILD_PACKAGES,
        )
