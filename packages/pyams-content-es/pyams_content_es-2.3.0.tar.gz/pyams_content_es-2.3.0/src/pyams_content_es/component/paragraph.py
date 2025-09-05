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

"""PyAMS_content_es.component.paragraph module

This module defines the adapters which are used to handle paragraphs indexation.
"""

from pyams_content.component.paragraph.interfaces import IBaseParagraph, IParagraphContainerTarget
from pyams_content.component.paragraph.interfaces.group import IParagraphsGroup
from pyams_content.component.paragraph.interfaces.html import IHTMLParagraph, IRawParagraph
from pyams_content_es.component import get_index_values, html_to_index
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config
from pyams_utils.finder import find_objects_providing
from pyams_utils.registry import get_pyramid_registry

__docformat__ = 'restructuredtext'


@adapter_config(name='body',
                required=IParagraphContainerTarget,
                provides=IDocumentIndexInfo)
def paragraph_container_index_info(context, adapters=None):
    """Paragraph container index info"""
    body = {}
    registry = get_pyramid_registry()
    for paragraph in find_objects_providing(context, IBaseParagraph):
        if (not paragraph.visible) or IParagraphsGroup.providedBy(paragraph):
            continue
        for name, info in registry.getAdapters((paragraph,), IDocumentIndexInfo):
            if name:
                if 'body' in info:
                    info = info['body']
                else:
                    continue
            for lang, body_info in info.items():
                body[lang] = f"{body.get(lang, '')}\n{body_info}"
    return {
        'body': body
    }


@adapter_config(required=IBaseParagraph,
                provides=IDocumentIndexInfo)
def base_paragraph_index_info(context):
    """Base paragraph index info"""
    info = {}
    get_index_values(context, info,
                     i18n_fields=('title',))
    return info


@adapter_config(required=IParagraphsGroup,
                provides=IDocumentIndexInfo)
def paragraphs_group_index_info(context):
    """Paragraphs group index info"""
    info = base_paragraph_index_info(context)
    paragraphs_info = paragraph_container_index_info(context)
    for lang, body in paragraphs_info.get('body', {}).items():
        info[lang] += f"\n{body}"
    return info


@adapter_config(required=IRawParagraph,
                provides=IDocumentIndexInfo)
@adapter_config(required=IHTMLParagraph,
                provides=IDocumentIndexInfo)
def html_paragraph_index_info(context):
    """HTML paragraph index info"""
    info = base_paragraph_index_info(context)
    get_index_values(context, info,
                     i18n_fields=(('body', html_to_index),))
    return info
