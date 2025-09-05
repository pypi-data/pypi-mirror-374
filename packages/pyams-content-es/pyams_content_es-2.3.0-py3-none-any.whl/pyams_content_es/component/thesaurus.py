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

"""PyAMS_content_es.component.thesaurus module

This module defines adapters which are used to handle thesaurus terms indexation.
"""

__docformat__ = 'restructuredtext'

from zope.intid import IIntIds

from pyams_content.component.thesaurus import ICollectionsInfo, ICollectionsTarget, ITagsInfo, \
    ITagsTarget, IThemesInfo, IThemesTarget
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config
from pyams_utils.list import unique
from pyams_utils.registry import get_utility


def get_term_ids(terms):
    """Term ID getter"""
    intids = get_utility(IIntIds)
    return list(map(intids.queryId, unique(terms)))


@adapter_config(name='tags',
                required=ITagsTarget,
                provides=IDocumentIndexInfo)
def tags_index_info(context):
    """Tags document index info"""
    tags = ITagsInfo(context).tags or ()
    return {
        'tags': get_term_ids(tags)
    }


@adapter_config(name='themes',
                required=IThemesTarget,
                provides=IDocumentIndexInfo)
def themes_index_info(context):
    """Themes document index info"""
    terms= []
    parents = []
    synonyms = []
    associations = []
    for term in IThemesInfo(context).themes or ():
        terms.append(term)
        if term.usage is not None:
            terms.append(term.usage)
        parents.extend(term.get_parents())
        synonyms.extend(term.used_for)
        associations.extend(term.associations)
    return {
        'themes': {
            'terms': get_term_ids(terms),
            'parents': get_term_ids(parents),
            'synonyms': get_term_ids(synonyms),
            'associations': get_term_ids(associations)
        }
    }


@adapter_config(name='collections',
                required=ICollectionsTarget,
                provides=IDocumentIndexInfo)
def collections_index_info(context):
    """Collections document index info"""
    collections = ICollectionsInfo(context).collections or ()
    return {
        'collections': get_term_ids(collections)
    }
