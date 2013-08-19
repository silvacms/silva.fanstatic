# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging
import Globals
import fanstatic

from zope.interface.interfaces import IInterface
from zope.testing.cleanup import addCleanUp


logger = logging.getLogger('silva.fanstatic')
INTERFACES_RESOURCES = {}
FANSTATIC_SETTINGS = {}

addCleanUp(INTERFACES_RESOURCES.clear)
addCleanUp(FANSTATIC_SETTINGS.clear)

def _set_settings(settings):
    FANSTATIC_SETTINGS.update(settings)
    mode = None
    if 'debug' in FANSTATIC_SETTINGS:
        mode = fanstatic.DEBUG
        del FANSTATIC_SETTINGS['debug']
    if 'minified' in FANSTATIC_SETTINGS:
        if mode is None:
            mode = fanstatic.MINIFIED
        del FANSTATIC_SETTINGS['minified']
    FANSTATIC_SETTINGS['mode'] = mode

def _get_settings():
    if FANSTATIC_SETTINGS:
        return FANSTATIC_SETTINGS.copy()
    if Globals.DevelopmentMode:
        return {'mode': fanstatic.DEBUG}
    return {'mode': fanstatic.MINIFIED,
            'bundle': True}

def get_inclusion(needed, resources=None):
    """Get a fanstatic ``Inclusion``. This can be used to get
    resources URL.
    """
    settings = _get_settings()
    return fanstatic.Inclusion(
        needed,
        resources=resources,
        mode=settings.get('mode', None),
        bundle=settings.get('bundle', False))


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
