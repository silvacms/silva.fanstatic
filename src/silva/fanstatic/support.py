# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from __future__ import absolute_import

from five import grok
from zope.interface import Interface, implements
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserView
import fanstatic

from silva.fanstatic.interfaces import ISubscribedResource
from silva.fanstatic.interfaces import IZopeResource
from silva.core.views.interfaces import IVirtualSite

from infrae.wsgi.interfaces import IPublicationAfterRender

from ZPublisher.interfaces import IPubFailure, IPubSuccess

_marker = object()


class ZopeFanstaticResource(object):
    # Hack to get ++resource++foo/bar/baz.jpg *paths* working in Zope
    # Pagetemplates. Note that ++resource+foo/bar/baz.jpg *URLs* will
    # not work with this hack!
    #
    # The ZopeFanstaticResource class also implements an __getitem__()
    # / get() interface, to support rendering URLs to resources from
    # code.

    implements(IZopeResource, ITraversable, IAbsoluteURL)

    def __init__(self, request, library, name=''):
        self.request = request
        self.library = library
        self.name = name

    def get(self, name, default=_marker):
        # XXX return default if given, or NotFound (or something) when
        # not, in case name is not resolved to an actual resource.
        name = '%s/%s' % (self.name, name)
        return ZopeFanstaticResource(self.request, self.library, name=name)

    def traverse(self, name, furtherPath):
        return self.get(name)

    def __getitem__(self, name):
        resource = self.get(name, None)
        if resource is None:
            raise KeyError(name)
        return resource

    def __str__(self):
        needed = fanstatic.get_needed()
        if not needed.has_base_url():
            needed.set_base_url(IVirtualSite(self.request).get_root_url())
        return needed.library_url(self.library) + self.name

    __call__ = __str__


class Resources(grok.ViewletManager):
    grok.context(Interface)
    grok.name('resources')

    def update(self):
        pass

    def render(self):
        return u''


@grok.subscribe(IPublicationAfterRender)
def inject_resources(event):
    if IBrowserView.providedBy(event.content):
        grok.queryMultiSubscriptions(
            (event.request, event.content), ISubscribedResource)


@grok.subscribe(IPubSuccess)
@grok.subscribe(IPubFailure)
def set_base_url(event):
    needed = fanstatic.get_needed()
    if not needed.has_resources():
        return
    if not needed.has_base_url():
        needed.set_base_url(IVirtualSite(event.request).get_root_url())
