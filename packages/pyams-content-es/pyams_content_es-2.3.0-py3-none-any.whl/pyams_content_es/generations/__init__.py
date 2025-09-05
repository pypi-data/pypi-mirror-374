#
# Copyright (c) 2015-2022 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_content_es.generations module

This module defines utilities required for Elasticsearch
integration.
"""

__docformat__ = 'restructuredtext'

from pyams_content_es.interfaces import IContentIndexerUtility, INDEXER_NAME
from pyams_site.generations import check_required_utilities
from pyams_site.interfaces import ISiteGenerations
from pyams_utils.registry import utility_config


REQUIRED_UTILITIES = (
    (IContentIndexerUtility, '', None, INDEXER_NAME),
)


@utility_config(name='PyAMS content ES', provides=ISiteGenerations)
class ContentIndexerGenerationsChecker:
    """Elasticsearch content indexer generations checker"""

    order = 70
    generation = 1

    def evolve(self, site, current=None):
        """Check for required utilities"""
        check_required_utilities(site, REQUIRED_UTILITIES)
