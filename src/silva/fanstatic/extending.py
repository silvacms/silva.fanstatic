# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

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
            logger.warning("Not including non-grokked resource %s" % identifier)
            return
        return resource.need()
    if hasattr(resource, 'need'):
        # There are no check possible ...
        resource.need()
