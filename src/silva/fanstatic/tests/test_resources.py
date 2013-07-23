
import unittest

from silva.fanstatic import Snippet, ExternalResource

class ResourceTestCase(unittest.TestCase):

    def test_snippet(self):
        # If two Snippet are added inside the same set, you
        # only get 1.
        css = Snippet(css="body {color: red}")
        self.assertEqual(len(set([Snippet(css="body {color: red}"), css])), 1)

    def test_external_resource(self):
        # If two ExternalResources are added inside the same set, you
        # only get 1.
        js = ExternalResource(js="http://silvacms.org/tracker.js")
        self.assertEqual(len(set([js, js])), 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ResourceTestCase))
    return suite
