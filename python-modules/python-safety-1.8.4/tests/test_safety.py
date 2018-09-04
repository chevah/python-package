#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_safety
----------------------------------

Tests for `safety` module.
"""


import sys
import unittest
from contextlib import contextmanager
from click.testing import CliRunner

from safety import safety
from safety import cli
from safety import formatter
from safety import util
import os
import json
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from safety.util import read_requirements

class TestSafetyCLI(unittest.TestCase):

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli)
        assert result.exit_code == 0
        assert 'Usage:' in result.output
        help_result = runner.invoke(cli.cli, ['--help'])
        assert help_result.exit_code == 0
        assert '--help' in help_result.output


class TestFormatter(unittest.TestCase):

    def test_get_terminal_size(self):
        try:
            formatter.get_terminal_size()
        except TypeError as e:
            self.fail(e)

    def test_report_json(self):
        test_arr = [['libfoo'],['libbar']]
        json_report = formatter.report(test_arr, full=False, json_report=True)
        assert json.loads(json_report) == test_arr

    def test_get_used_db(self):
        assert 'default DB' == formatter.get_used_db(key=None, db='')
        assert 'pyup.io\'s DB' == formatter.get_used_db(key='foo', db='')
        assert 'local DB' == formatter.get_used_db(key=None, db='/usr/local/some-db')


class TestSafety(unittest.TestCase):

    def test_check_from_file(self):
        reqs = StringIO("Django==1.8.1")
        packages = util.read_requirements(reqs)

        vulns = safety.check(
            packages=packages,
            db_mirror=os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "test_db"
            ),
            cached=False,
            key=False,
            ignore_ids=[]
        )
        self.assertEqual(len(vulns), 2)

    def test_multiple_versions(self):
        reqs = StringIO("Django==1.8.1\n\rDjango==1.7.0")
        packages = util.read_requirements(reqs)

        vulns = safety.check(
            packages=packages,
            db_mirror=os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "test_db"
            ),
            cached=False,
            key=False,
            ignore_ids=[]
        )
        self.assertEqual(len(vulns), 4)
    def test_check_live(self):
        reqs = StringIO("insecure-package==0.1")
        packages = util.read_requirements(reqs)

        vulns = safety.check(
            packages=packages,
            db_mirror=False,
            cached=False,
            key=False,
            ignore_ids=[]
        )
        self.assertEqual(len(vulns), 1)

    def test_check_live_cached(self):
        reqs = StringIO("insecure-package==0.1")
        packages = util.read_requirements(reqs)

        vulns = safety.check(
            packages=packages,
            db_mirror=False,
            cached=True,
            key=False,
            ignore_ids=[]
        )
        self.assertEqual(len(vulns), 1)

        reqs = StringIO("insecure-package==0.1")
        packages = util.read_requirements(reqs)
        # make a second call to use the cache
        vulns = safety.check(
            packages=packages,
            db_mirror=False,
            cached=True,
            key=False,
            ignore_ids=[]
        )
        self.assertEqual(len(vulns), 1)


class ReadRequirementsTestCase(unittest.TestCase):

    def test_unpinned_vcs_requirement(self):
        """
        https://github.com/pyupio/safety/issues/72
        """
        # this shouldn't raise an error
        content = StringIO("-e git+https://github.com/jdunck/python-unicodecsv#egg=unicodecsv")
        result = list(read_requirements(content))
        self.assertEqual(len(result), 0)

