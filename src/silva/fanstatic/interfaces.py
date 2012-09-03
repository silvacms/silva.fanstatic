# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt


from zope.interface import Interface


class ISubscribedResource(Interface):
    pass


class IZopeResource(Interface):

    def get(name, default):
        pass

    def __getitem__(self, name):
        pass
