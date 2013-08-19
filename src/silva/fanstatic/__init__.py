# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.fanstatic.extending import need, get_inclusion
from silva.fanstatic.resources import ExternalResource, Snippet
from fanstatic import Group
from fanstatic import get_needed

__all__ = [
    'need', 'get_inclusion', 'get_needed',
    'ExternalResource', 'Snippet', 'Group']


# Patch fanstatic with missing API calls during testing
from fanstatic.core import DummyNeededResources

DummyNeededResources.has_base_url = lambda self: True
DummyNeededResources.set_base_url = lambda self, url: None
DummyNeededResources.library_url = lambda self, library: u'/'.join(('http://test', library.name))
