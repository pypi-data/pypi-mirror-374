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

import locale

from zope.intid.interfaces import IIntIds

from pyams_content.feature.filter import ICollectionsFilter, IContentTypesFilter, IFilter, ITagsFilter, IThemesFilter, \
    ITitleFilter
from pyams_content.feature.filter.interfaces import FILTER_SORTING, IAggregatedPortletRendererSettings, IFilterProcessor
from pyams_content.feature.filter.processor import BaseFilterProcessor
from pyams_layer.interfaces import IPyAMSLayer
from pyams_utils.adapter import adapter_config
from pyams_utils.registry import get_utility

__docformat__ = 'restructuredtext'


SORTING_MODES = {
    FILTER_SORTING.ALPHA.value: lambda x: locale.strxfrm(x['label']),
    FILTER_SORTING.ALPHA_DESC.value: lambda x: locale.strxfrm(x['label']),
    FILTER_SORTING.COUNT.value: lambda x: (x['doc_count'], locale.strxfrm(x['label'])),
    FILTER_SORTING.COUNT_DESC.value: lambda x: (x['doc_count'], locale.strxfrm(x['label'])),
    FILTER_SORTING.MANUAL.value: lambda x: x.get('order', 0)
}


def get_sorting_key(sorting_mode):
    return SORTING_MODES.get(sorting_mode, 'alpha_asc')


@adapter_config(required=(IFilter, IPyAMSLayer, IAggregatedPortletRendererSettings),
                provides=IFilterProcessor)
class EsBaseFilterProcessor(BaseFilterProcessor):
    """Elasticsearch base filter processor"""

    def get_aggregations(self, aggregations):
        result = self.convert_aggregations(aggregations)
        sorting_mode = self.filter.sorting_mode
        sorting_key = get_sorting_key(sorting_mode)
        if sorting_key:
            result.sort(key=sorting_key,
                        reverse=sorting_mode.endswith('_desc'))
        return result

    def convert_aggregations(self, aggregations):
        result = []
        for item in aggregations:
            result.append({
                'key': item.key,
                'label': item.key,
                'doc_count': item.doc_count
            })
        return result


@adapter_config(required=(IContentTypesFilter, IPyAMSLayer, IAggregatedPortletRendererSettings),
                provides=IFilterProcessor)
class ContentTypeFilterProcessor(EsBaseFilterProcessor):
    """Content-type filter processor"""

    def process(self, aggregations, filter_type=None):
        return super().process(aggregations, self.filter.content_mode)


@adapter_config(required=(ITitleFilter, IPyAMSLayer, IAggregatedPortletRendererSettings),
                provides=IFilterProcessor)
class TitleFilterProcessor(EsBaseFilterProcessor):
    """Title filter processor"""


class EsBaseThesaurusFilterProcessor(EsBaseFilterProcessor):
    """Base filter aggregation processor"""

    def convert_aggregations(self, aggregations):
        """Convert aggregation raw data in human form"""
        intids = get_utility(IIntIds)
        result = []
        for item in aggregations:
            tag_id = int(item.key)
            tag_object = intids.queryObject(tag_id)
            if tag_object:
                if self.filter.extract_name and (self.filter.extract_name not in tag_object.extracts or ()):
                    continue
                result.append({
                    'key': tag_object.label,
                    'label': tag_object.public_title,
                    'order': tag_object.order or 0,
                    'doc_count': item.doc_count
                })
        return result


@adapter_config(required=(ITagsFilter, IPyAMSLayer, IAggregatedPortletRendererSettings),
                provides=IFilterProcessor)
class TagsFilterProcessor(EsBaseThesaurusFilterProcessor):
    """Tags filter processor"""


@adapter_config(required=(IThemesFilter, IPyAMSLayer, IAggregatedPortletRendererSettings),
                provides=IFilterProcessor)
class ThemeFilterProcessor(EsBaseThesaurusFilterProcessor):
    """Themes filter processor"""


@adapter_config(required=(ICollectionsFilter, IPyAMSLayer, IAggregatedPortletRendererSettings),
                provides=IFilterProcessor)
class CollectionFilterProcessor(EsBaseThesaurusFilterProcessor):
    """Collections filter processor"""
