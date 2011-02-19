

from zope.interface import Interface


class ISubscribedResource(Interface):
    pass


class IZopeResource(Interface):

    def get(name, default):
        pass

    def __getitem__(self, name):
        pass
