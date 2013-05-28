
import unittest
import doctest
from Products.Silva.testing import FunctionalLayer, suite_from_package

globs = {
    'get_browser': FunctionalLayer.get_browser,
    'grok': FunctionalLayer.grok,}


def create_test(build_test_suite, name):
    test =  build_test_suite(
        name,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
    test.layer = FunctionalLayer
    return test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        suite_from_package('silva.fanstatic.tests.dependencies', create_test))
    return suite
