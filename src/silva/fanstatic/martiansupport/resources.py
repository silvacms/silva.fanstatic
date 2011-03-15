# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from martian.error import GrokError
from zope import component
from zope.component.interface import provideInterface
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface.interface import InterfaceClass
import martian
import fanstatic

from silva.core.conf.martiansupport import directives as silvaconf
from silva.fanstatic.interfaces import ISubscribedResource
from silva.fanstatic.integration import ZopeFanstaticResource
from silva.fanstatic.extending import INTERFACES_RESOURCES

_marker = object()


def is_fanstatic_resource(resource):
    """Return true if resource is a fanstatic resource.
    """
    return (isinstance(resource, fanstatic.Resource) or
            isinstance(resource, fanstatic.GroupResource))


def get_fanstatic_resource(library, resources):
    """Return a fanstatic resource from library out of the resources
    list.
    """
    dependencies = []
    for resource in resources:
        if is_fanstatic_resource(resource):
            dependencies.append(resource)
        else:
            dependencies.append(fanstatic.Resource(library, resource))
    return fanstatic.GroupResource(dependencies)


def get_fanstatic_library(module_info):
    """Return the fanstatic library associated to the given module.
    """
    registry = fanstatic.get_library_registry()
    if module_info.package_dotted_name in registry:
        library = registry[module_info.package_dotted_name]
    else:
        library = fanstatic.Library(
            module_info.package_dotted_name, 'static')
        # Fix the correct path
        library.path = module_info.getResourcePath('static')
        # Register the new library to fanstatic
        registry.add(library)
    return library


def create_resource_subscriber(resource):
    """Return a subscription that require the resource content.
    """

    def subscriber(*args):
        resource.need()

    return subscriber


def list_base_layers(layer):
    """List all layers used by the given layer.
    """
    if IInterface.providedBy(layer) and layer.extends(IBrowserRequest):
        for base in layer.__bases__:
            if base in (
                IDefaultBrowserLayer, IBrowserSkinType, IBrowserRequest, Interface):
                continue
            need_parent = yield base
            if need_parent:
                need_base_parents = None
                base_parents = list_base_layers(base)
                while True:
                    try:
                        need_base_parents = yield base_parents.send(need_base_parents)
                    except StopIteration:
                        break


class ResourceIncludeGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)

    def grok(self, name, interface, module_info, config, **kw):
        resources = silvaconf.resource.bind(default=_marker).get(interface)
        if resources is _marker:
            return False
        if not interface.extends(IDefaultBrowserLayer):
            raise GrokError(
                "A resource can be included only on a layer.", interface)

        # Get the fanstatic library
        library = get_fanstatic_library(module_info)

        # Create a group with all the resources
        resource = get_fanstatic_resource(library,  resources)
        INTERFACES_RESOURCES[interface.__identifier__] = resource

        context = silvaconf.only_for.bind().get(interface)
        factory = create_resource_subscriber(resource)

        config.action(
            discriminator = None,
            callable = component.provideSubscriptionAdapter,
            args = (factory, (interface, context), ISubscribedResource))
        config.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', interface))
        config.action(
            discriminator = ('solve_dependencies', interface),
            callable = self.solve_dependencies,
            args = (interface, resource))
        return True

    def solve_dependencies(self, interface, resource):
        try:
            need_parent = None
            parents = list_base_layers(interface)
            while True:
                dependency = parents.send(need_parent)
                identifier = dependency.__identifier__
                if identifier in INTERFACES_RESOURCES:
                    resource.depends.insert(0, INTERFACES_RESOURCES[identifier])
                    need_parent = False
                else:
                    need_parent = True
        except StopIteration:
            pass


def create_factory(library):
    """Return a resource factory to browser the associated library.
    """

    def factory(request):
        return ZopeFanstaticResource(request, library)

    return factory


class StaticDirectoryGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        # we're only interested in static resources if this module
        # happens to be a package
        if not module_info.isPackage():
            return False

        # Get the fanstatic library
        library = get_fanstatic_library(module_info)

        factory = create_factory(library)
        adapts = (IBrowserRequest,)
        provides = Interface
        config.action(
            discriminator = ('adapter', adapts, provides, library.name),
            callable = component.provideAdapter,
            args = (factory, adapts, provides, library.name))
        return True
