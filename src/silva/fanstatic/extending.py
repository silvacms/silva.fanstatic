# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface.interfaces import IInterface
from zope.testing.cleanup import addCleanUp

INTERFACES_RESOURCES = {}

addCleanUp(INTERFACES_RESOURCES.clear)


def need(resource):
    """Require given resource.
    """
    if IInterface.providedBy(resource):
        resource = INTERFACES_RESOURCES.get(resource.__identifier__)
        assert resource is not None, "Unknow resource set"
    resource.need()
