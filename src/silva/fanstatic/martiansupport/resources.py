# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from fanstatic import Library, Resource, GroupResource, get_library_registry
from five import grok
from martian.error import GrokError
from zope import component
from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import martian

from silva.core.conf.martiansupport import directives as silvaconf
from silva.fanstatic.interfaces import ISubscribedResource
from silva.fanstatic.resources import ZopeFanstaticResource

_marker = object()


def is_fanstatic_resource(resource):
    return (isinstance(resource, Resource) or
            isinstance(resource, GroupResource))


def create_resource_subscriber(resources, order):

    class ResourceSubscriber(object):
        grok.order(order)
        grok.implements(ISubscribedResource)

        def __init__(self, *args):
            pass

        def __call__(self):
            resources.need()

    return ResourceSubscriber


class ResourceIncludeGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)

    def get_fanstatic_resource(self, library, resources):
        dependencies = []
        for resource in resources:
            if is_fanstatic_resource(resource):
                dependencies.append(resource)
            else:
                dependencies.append(Resource(library, resource))
        return GroupResource(dependencies)

    def grok(self, name, interface, module_info, config, **kw):
        resources = silvaconf.resource.bind(default=_marker).get(interface)
        if resources is _marker:
            return False
        if not interface.extends(IDefaultBrowserLayer):
            raise GrokError(
                "A resource can be included only on a layer.", interface)

        registry = get_library_registry()
        if module_info.package_dotted_name in registry:
            library = registry[module_info.package_dotted_name]
        else:
            library = Library(module_info.package_dotted_name, 'static')
            # Fix the correct path
            library.path = module_info.getResourcePath('static')
            # Register the new library to fanstatic
            registry.add(library)

        # Create a group with all the resources
        resources = self.get_fanstatic_resource(library,  resources)

        context = silvaconf.only_for.bind().get(interface)
        factory = create_resource_subscriber(
            resources, len(interface.__iro__))

        config.action(
            discriminator = None,
            callable = component.provideSubscriptionAdapter,
            args = (factory, (interface, context), ISubscribedResource))

        return True


def create_factory(library):

    def factory(request):
        return ZopeFanstaticResource(request, library)

    return factory


class StaticDirectoryGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        # we're only interested in static resources if this module
        # happens to be a package
        if not module_info.isPackage():
            return False

        registry = get_library_registry()
        if module_info.package_dotted_name in registry:
            library = registry[module_info.package_dotted_name]
        else:
            library = Library(module_info.package_dotted_name, 'static')
            # Fix the correct path
            library.path = module_info.getResourcePath('static')
            # Register the new library to fanstatic
            registry.add(library)

        factory = create_factory(library)
        adapts = (IBrowserRequest,)
        provides = Interface
        config.action(
            discriminator = ('adapter', adapts, provides, library.name),
            callable = component.provideAdapter,
            args = (factory, adapts, provides, library.name))
        return True
