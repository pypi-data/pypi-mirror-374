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

from pyams_content.feature.filter import ICollectionsFilter, IContentTypesFilter, IFilterAggregate, ITagsFilter, \
    IThemesFilter, ITitleFilter
from pyams_content.feature.filter.interfaces import FILTER_SORTING
from pyams_i18n.interfaces import INegotiator
from pyams_thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusExtracts
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces import ICacheKeyValue
from pyams_utils.registry import get_pyramid_registry, get_utility, query_utility

__docformat__ = 'restructuredtext'


SORTING_PARAMS = {
    FILTER_SORTING.ALPHA.value:      {'_key': 'asc'},
    FILTER_SORTING.ALPHA_DESC.value: {'_key': 'desc'},
    FILTER_SORTING.COUNT.value:      {'_count': 'asc'},
    FILTER_SORTING.COUNT_DESC.value: {'_count': 'desc'}
}


def get_sorting_params(sorting_mode):
    """Returns the sorting parameters for Elasticsearch queries based on the provided sorting option.

    :param sorting_mode: A string representing the desired sorting option.
    :return: A dictionary representing the Elasticsearch sorting parameters.
    """
    return SORTING_PARAMS.get(sorting_mode, {'_key': 'asc'})


@adapter_config(required=IContentTypesFilter,
                provides=IFilterAggregate)
def content_type_filter_aggregate(context):
    """Content-type filter aggregate getter"""
    content_mode = context.content_mode
    sorting_params = get_sorting_params(context.sorting_mode)
    registry = get_pyramid_registry()
    return {
        'name': context.filter_name,
        'type': 'terms',
        'params': {
            'field': registry.settings.get(f'pyams_content_es.filter.{content_mode}.field_name',
                                           content_mode),
            'size': 100,
            'order': sorting_params
        }
    }


@adapter_config(required=ITitleFilter,
                provides=IFilterAggregate)
def title_filter_aggregate(context):
    """Title filter aggregate getter"""
    sorting_params = get_sorting_params(context.sorting_mode)
    registry = get_pyramid_registry()
    field_name = registry.settings.get('pyams_content_es.filter.title.field_name')
    if not field_name:
        negotiator = get_utility(INegotiator)
        field_name = f'title.{negotiator.server_language}.keyword'
    return {
        'name': context.filter_name,
        'type': 'terms',
        'params': {
            'field': field_name,
            'size': 100,
            'order': sorting_params
        }
    }


def get_terms_aggregate(context, field_name):
    """Helper function used to build thesaurus filter aggregate"""
    thesaurus = query_utility(IThesaurus, name=context.thesaurus_name)
    if thesaurus is None:
        return None
    sorting_params = get_sorting_params(context.sorting_mode)
    registry = get_pyramid_registry()
    filter_aggregate = {
        'name': context.filter_name,
        'type': 'terms',
        'params': {
            'field': registry.settings.get(f'pyams_content_es.filter.{field_name}.field_name',
                                           field_name),
            'size': 100,
            'order': sorting_params
        }
    }
    if context.extract_name:
        extract = IThesaurusExtracts(thesaurus).get(context.extract_name)
        if extract is not None:
            terms = list(extract.terms_ids)
            if terms:
                filter_aggregate['params']['include'] = terms
    return filter_aggregate


@adapter_config(required=ITagsFilter,
                provides=IFilterAggregate)
def tags_filter_aggregate(context):
    """tags filter aggregate getter"""
    return get_terms_aggregate(context, 'tags')


@adapter_config(required=IThemesFilter,
                provides=IFilterAggregate)
def theme_filter_aggregate(context):
    """theme filter aggregate getter"""
    return get_terms_aggregate(context, 'themes.terms')


@adapter_config(required=ICollectionsFilter,
                provides=IFilterAggregate)
def collection_filter_aggregate(context):
    """Content-type filter aggregate getter"""
    return get_terms_aggregate(context, 'collections')
