#! /usr/bin/env python3.7

try:
    from ..conway import strife
except ImportError:
    import conway.strife as strife

from parameterized import parameterized
# from unittest.mock import patch # for sys.stderr string patching
# from nose.tools import raises
# from io import StringIO # for sys.stderr string patching
import unittest
# import argparse
# import random


def gen_args_obj(**kwargs):

    class Args(object):
        pass

    args = Args()
    for k, v in kwargs.items():
        setattr(args, k, v)

    return args


class ConwayUnitTests(unittest.TestCase):

    @unittest.skip('Not yet written')
    @parameterized.expand([], skip_on_empty=True)
    def test_main_conway_through(self):
        strife.main(strife.parse_args(['-s']))
        assert True


class ConwayFunctionalTests(unittest.TestCase):

    def test_main_conway_through(self):
        strife.main(strife.parse_args(['-sv']))
        assert True
