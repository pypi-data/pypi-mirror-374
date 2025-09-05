# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from pyams_content.component.cards.interfaces import ICardsParagraph
from pyams_content_es.component import get_index_values
from pyams_content_es.component.paragraph import base_paragraph_index_info
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@adapter_config(required=ICardsParagraph,
                provides=IDocumentIndexInfo)
def cards_paragraph_index_info(context):
    """Cards paragraph index info"""
    info = base_paragraph_index_info(context)
    for card in context.get_visible_items():
        get_index_values(card, info,
                         i18n_fields=('title', 'body'))
        
    return info
