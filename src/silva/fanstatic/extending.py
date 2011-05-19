# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from zope.interface.interfaces import IInterface
from zope.testing.cleanup import addCleanUp


logger = logging.getLogger('silva.fanstatic')
INTERFACES_RESOURCES = {}

addCleanUp(INTERFACES_RESOURCES.clear)


def need(resource):
    """Require given resource.
    """
    if IInterface.providedBy(resource):
        identifier = resource.__identifier__
        resource = INTERFACES_RESOURCES.get(identifier)
        if resource is None:
            logger.warning("Not including non-grokked resource set %s" % identifier)
            return
    resource.need()
