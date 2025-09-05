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

"""PyAMS_content_es.component.links module

This module defines the adapters which are used to handle links indexation.
"""

from pyams_content.component.association import IAssociationContainerTarget
from pyams_content.component.association.interfaces import IAssociationContainer
from pyams_content.component.links import IBaseLink
from pyams_content_es.component import get_index_values
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@adapter_config(name='links',
                required=IAssociationContainerTarget,
                provides=IDocumentIndexInfo)
def association_container_target_link_index_info(context):
    """Internal and external links index info"""
    index_info = {}
    for link in IAssociationContainer(context).get_visible_items():
        if not IBaseLink.providedBy(link):
            continue
        get_index_values(link, index_info,
                         i18n_fields=('title', 'description'))
    return {
        'body': index_info
    }
