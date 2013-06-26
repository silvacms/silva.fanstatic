
from five import grok
from zope.interface import Interface

from silva.fanstatic.resources import ExternalResource


class FullView(grok.View):
    grok.name('full.html')
    grok.context(Interface)

    def render(self):
        framework = ExternalResource(
            'http://silvacms.org/framework.js')
        js = ExternalResource(
            'http://silvacms.org/tracker.js',
            depends=[framework])
        js.need()
        js.need()               # We add it twice
        css = ExternalResource(
            'http://infr.ae/tracker.css',
            category='css')
        css.need()
        return u'<html><head></head><body>Hello</body></html>'
