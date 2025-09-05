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

"""PyAMS_content_es.component main module

"""

from pyams_i18n.interfaces import II18nManager, INegotiator
from pyams_utils.html import html_to_text
from pyams_utils.registry import get_utility

__docformat__ = 'restructuredtext'


_marker = object()


def html_to_index(value):
    """HTML converter to index value"""
    return html_to_text(value).replace(chr(13), '')


def get_index_values(context, output, fields=None, i18n_fields=None, sep='\n'):
    """Get index values from context"""
    i18n_manager = II18nManager(context, None)
    if i18n_manager is None:
        negotiator = get_utility(INegotiator)
        languages = negotiator.offered_languages
    else:
        languages = i18n_manager.get_languages()
    # simple fields getter
    for field in (fields or ()):
        if isinstance(field, tuple):
            field, converter = field
        else:
            converter = None
        value = getattr(context, field, _marker)
        if (not value) or (value is _marker):
            continue
        if converter is not None:
            value = converter(value)
        for lang in languages:
            output[lang] = f"{output.get(lang, '')}{sep}" \
                           f"{value}"
    # i18n fields getter
    for field in (i18n_fields or ()):
        if isinstance(field, tuple):
            field, converter = field
        else:
            converter = None
        value = getattr(context, field, _marker)
        if (not value) or (value is _marker):
            continue
        for lang, i18n_value in value.items():
            if not i18n_value:
                continue
            if converter is not None:
                i18n_value = converter(i18n_value)
            output[lang] = f"{output.get(lang, '')}{sep}" \
                           f"{i18n_value}"
