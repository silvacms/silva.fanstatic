
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from silva.core import conf as silvaconf
from silva.fanstatic import need
from five import grok


class IBaseLayer(IDefaultBrowserLayer):
    silvaconf.resource('base.css')


class IFeatureALayer(IBaseLayer):
    silvaconf.resource('featurea.css')


class IFeatureBLayer(IDefaultBrowserLayer):
    silvaconf.resource('featureb.css')


class IFullLayer(IFeatureALayer, IFeatureBLayer):
    silvaconf.resource('full.css')


class FullView(grok.View):
    grok.name('full.html')
    grok.context(Interface)

    def render(self):
        need(IFullLayer)
        return u'<html><head></head><body>Hello</body></html>'
