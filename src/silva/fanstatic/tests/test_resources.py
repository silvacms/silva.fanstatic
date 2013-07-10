
import unittest
from silva.fanstatic import Snippet, ExternalResource


CSS = "body {color: red}"
JS_URL = "http://silvacms.org/tracker.js"

class ResourceTestCase(unittest.TestCase):

    def test_snippet(self):
        # If two Snippet are added inside the same set, you
        # only get 1.
        css = Snippet(CSS, category='css')
        self.assertEqual(
            css.ext,
            '.css')
        self.assertEqual(
            len(set([Snippet(CSS, category='css'), css])),
            1)
        self.assertEqual(
            css.render(None),
            '<style type="text/css">body {color: red}</style>')

    def test_external_resource(self):
        # If two ExternalResources are added inside the same set, you
        # only get 1.
        js = ExternalResource(JS_URL, category='js')
        self.assertEqual(
            js.ext,
            '.js')
        self.assertEqual(
            len(set([ExternalResource(JS_URL, category='js'), js])),
            1)
        self.assertEqual(
            js.render(None),
            '<script type="text/javascript" src="http://silvacms.org/tracker.js"></script>')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ResourceTestCase))
    return suite
