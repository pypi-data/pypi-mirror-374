#
# Copyright (c) 2015-2024 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_*** module

"""

from pyams_content.component.illustration.interfaces import IIllustration, IIllustrationParagraph, IIllustrationTarget
from pyams_content_es.component import get_index_values
from pyams_content_es.component.paragraph import base_paragraph_index_info
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@adapter_config(name='illustration',
                required=IIllustrationTarget,
                provides=IDocumentIndexInfo)
def illustration_target_index_info(context):
    """Illustration target index info"""
    index_info = {}
    illustration = IIllustration(context)
    if illustration.has_data():
        index_info = base_paragraph_index_info(illustration)
        get_index_values(illustration, index_info,
                         fields=('author',),
                         i18n_fields=('description', 'alt_title'))
    return {
        'body': index_info
    }
    

@adapter_config(required=IIllustrationParagraph,
                provides=IDocumentIndexInfo)
def illustration_paragraph_index_info(context):
    """Illustration paragraph index info"""
    info = base_paragraph_index_info(context)
    get_index_values(context, info,
                     fields=('author',),
                     i18n_fields=('description', 'alt_title'))
    return info
