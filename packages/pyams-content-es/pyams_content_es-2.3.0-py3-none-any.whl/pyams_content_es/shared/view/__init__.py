#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_content_es.shared.view module

This module defines how shared content queries are handled when using an Elasticsearch
index.
"""

__docformat__ = 'restructuredtext'

from elasticsearch_dsl import A, AttrDict, Q, Search
from zope.interface import implementer

from pyams_catalog.query import CatalogResultSet
from pyams_content.shared.view import IViewQuery, IWfView
from pyams_content.shared.view.interfaces import RELEVANCE_ORDER, TITLE_ORDER
from pyams_content.shared.view.interfaces.query import END_PARAMS_MARKER
from pyams_content_es.interfaces import IContentIndexerUtility, IUserSearchSettings
from pyams_content_es.shared.view.interfaces import IEsViewQuery, IEsViewQueryParamsExtension, \
    IEsViewQueryPostFilterExtension, IEsViewQueryResultsFilterExtension, IEsViewUserPostFilter, IEsViewUserQuery
from pyams_elastic.include import get_client
from pyams_i18n.interfaces import INegotiator
from pyams_sequence.interfaces import ISequentialIntIds
from pyams_utils.adapter import ContextAdapter, adapter_config, get_adapter_weight
from pyams_utils.list import boolean_iter, unique_iter
from pyams_utils.registry import get_pyramid_registry, get_utility
from pyams_workflow.interfaces import IWorkflow


@adapter_config(required=IWfView,
                provides=IViewQuery)
@implementer(IEsViewQuery)
class EsViewQuery(ContextAdapter):
    """Elasticsearch view query"""

    def get_params(self, context, request=None, **kwargs):
        view = self.context
        registry = get_pyramid_registry()
        # check publication dates
        params = Q('range',
                   **{'workflow.effective_date': {'lte': 'now/m'}})
        # check workflow states
        if 'state' in kwargs:
            state = kwargs['state']
            if not isinstance(state, (list, tuple, set)):
                state = (state,)
            params &= Q('terms',
                        **{'workflow.status': state})
        else:
            wf_params = []
            for workflow in registry.getAllUtilitiesRegisteredFor(IWorkflow):
                wf_params.extend(workflow.visible_states)
            params &= Q('terms',
                        **{'workflow.status': wf_params})
        # check custom extensions
        get_all_params = True
        for name, adapter in sorted(registry.getAdapters((view,), IEsViewQueryParamsExtension),
                                    key=get_adapter_weight):
            for new_params in adapter.get_params(context, request):
                if new_params is None:
                    return None
                elif new_params is END_PARAMS_MARKER:
                    get_all_params = False
                    break
                else:
                    params &= new_params
            else:
                continue
            break
        # activate search
        params &= Q('bool',
                    must=Q('range',
                           **{'workflow.push_end_date': {'gte': 'now/m'}})) | \
                  Q('bool',
                    must_not=Q('exists',
                               **{'field': 'workflow.push_end_date'}))
        if get_all_params:
            # check content path
            content_path = view.get_content_path(context)
            if content_path is not None:
                params &= Q('term',
                            **{'parent_ids': content_path})
            # check content types
            if 'content_type' in kwargs:
                params &= Q('term',
                            **{'content_type': kwargs['content_type']})
            else:
                params &= Q('bool',
                            must_not=Q('terms',
                                       **{'content_type': tuple(view.get_ignored_types())}))
                content_types = view.get_content_types(context)
                if content_types:
                    params &= Q('terms',
                                **{'content_type': content_types})
            # check data types
            data_types = view.get_data_types(context)
            if data_types:
                params &= Q('terms',
                            **{'data_type': data_types})
            # check excluded content types
            content_types = view.get_excluded_content_types(context)
            if content_types:
                params &= Q('bool',
                            must_not=Q('terms',
                                       **{'content_type': content_types}))
            # check excluded data types
            data_types = view.get_excluded_data_types(context)
            if data_types:
                params &= Q('bool',
                            must_not=Q('terms',
                                       **{'data_type': data_types}))
            # check age limit
            age_limit = view.age_limit
            if age_limit:
                params &= Q('range',
                            **{
                                'workflow.content_publication_date': {
                                    'gte': f'now-{age_limit}d/m'
                                }
                            })
        return params

    def get_post_filters(self, context, request=None, **kwargs):
        registry = get_pyramid_registry()
        for name, adapter in sorted(registry.getAdapters((self.context,), IEsViewQueryPostFilterExtension),
                                    key=get_adapter_weight):
            yield from adapter.get_params(context, request)

    def get_results(self, context, sort_index, reverse, limit,
                    request=None, aggregates=None, settings=None, **kwargs):
        aggregations = {}
        registry = request.registry
        client = get_client(request)
        params = self.get_params(context, request, **kwargs)
        if params is None:
            items = CatalogResultSet([])
            total_count = 0
        else:
            # get post-filters (excluded from aggregations calculation)
            filters = Q()
            for filter in self.get_post_filters(context, request, **kwargs):
                filters &= filter
            search = Search(using=client.es, index=client.index) \
                .params(request_timeout=30) \
                .query(params) \
                .post_filter(filters) \
                .source(['internal_id'])
            if aggregates:
                for agg in aggregates:
                    search.aggs.bucket(agg['name'],
                                       A(agg['type'], **agg['params']))
            # Define sort order
            sort_values = []
            if (not sort_index) or (sort_index == RELEVANCE_ORDER):
                sort_values.append({
                    '_score': {
                        'order': 'desc'
                    }
                })
            elif sort_index == TITLE_ORDER:
                negotiator = get_utility(INegotiator)
                sort_values.append({
                    f'title.{negotiator.server_language}.keyword': {
                        'order': 'desc' if reverse else 'asc'
                    }
                })
            else:
                sort_values.append({
                    f'workflow.{sort_index}': {
                        'order': 'desc' if reverse else 'asc',
                        'unmapped_type': 'date'
                    }
                })
            if sort_values:
                search = search.sort(*sort_values)
            # Define limits
            if limit:
                search = search[:limit]
            else:
                search = search[:999]
            # Get query results
            results = search.execute()
            items = CatalogResultSet([result.internal_id for result in results.hits])
            aggregations = results.aggregations
            total_count = results.hits.total
            if isinstance(total_count, (dict, AttrDict)):
                total_count = results.hits.total['value']
        for name, adapter in sorted(registry.getAdapters((self.context,),
                                                         IEsViewQueryResultsFilterExtension),
                                    key=lambda x: x[1].weight):
            items = adapter.filter(context, items, request)
        return total_count, aggregations, unique_iter(items)


class BaseEsUserViewQueryExtension(ContextAdapter):
    """Base Elasticsearch user view query extension"""

    weight = 999
    query_interface = None

    def __new__(cls, context):
        if not context.allow_user_params:
            return None
        return ContextAdapter.__new__(cls)

    def get_params(self, context, request=None):
        """User params getter"""
        registry = get_pyramid_registry()
        for name, adapter in sorted(registry.getAdapters((self.context,), self.query_interface),
                                    key=get_adapter_weight):
            yield from adapter.get_user_params(request)


@adapter_config(name='user-params',
                required=IWfView,
                provides=IEsViewQueryParamsExtension)
class EsUserViewQueryParamsExtension(BaseEsUserViewQueryExtension):
    """Elasticsearch user view query params extension"""

    query_interface = IEsViewUserQuery


@adapter_config(name='user-params',
                required=IWfView,
                provides=IEsViewQueryPostFilterExtension)
class EsUserViewQueryPostFilterExtension(BaseEsUserViewQueryExtension):
    """Elasticsearch user view query post-filters extension"""

    query_interface = IEsViewUserPostFilter


class EsViewSimpleTermQuery(ContextAdapter):
    """Elasticsearch simple view term query adapter"""

    param_name = None
    field_name = None

    def get_user_params(self, request):
        params = request.params.getall(self.param_name)
        if params:
            registry = request.registry
            field_name = registry.settings.get(f'pyams_content_es.filter.{self.field_name}.field_name',
                                               self.field_name)
            yield Q('terms', **{field_name: params})


@adapter_config(name='content-type',
                required=IWfView,
                provides=IEsViewUserQuery)
class EsViewContentTypeQuery(EsViewSimpleTermQuery):
    """Search folder content-type query"""

    param_name = 'content_type'
    field_name = 'content_type'


@adapter_config(name='data-type',
                required=IWfView,
                provides=IEsViewUserQuery)
class EsViewDatatypeQuery(EsViewSimpleTermQuery):
    """Search folder data-type query"""

    param_name = 'data_type'
    field_name = 'data_type'


@adapter_config(name='facet-label',
                required=IWfView,
                provides=IEsViewUserQuery)
class EsViewFacetLabelQuery(EsViewSimpleTermQuery):
    """Search folder facet label query"""

    param_name = 'facet_label'
    field_name = 'facet_label'


@adapter_config(name='facet-type-label',
                required=IWfView,
                provides=IEsViewUserQuery)
class EsViewFacetTypeLabelQuery(EsViewSimpleTermQuery):
    """Search folder facet type label query"""

    param_name = 'facet_type_label'
    field_name = 'facet_type_label'


@adapter_config(name='title',
                required=IWfView,
                provides=IEsViewUserPostFilter)
class EsViewTitleQuery(EsViewSimpleTermQuery):
    """Search folder title query"""

    param_name = 'title'

    @property
    def field_name(self):
        negotiator = get_utility(INegotiator)
        return f'title.{negotiator.server_language}.keyword'


@adapter_config(name='user-search',
                required=IWfView,
                provides=IEsViewUserQuery)
class EsViewUserSearchQuery(ContextAdapter):
    """Elasticsearch user search query adapter"""

    @staticmethod
    def get_user_params(request):
        """User params getter"""
        fulltext = request.params.get('user_search')
        if fulltext:
            if fulltext.startswith('+'):
                sequence = get_utility(ISequentialIntIds)
                oid = sequence.get_full_oid(fulltext)
                yield Q('term',
                        **{'reference_id': oid})
            else:
                indexer = get_utility(IContentIndexerUtility)
                settings = IUserSearchSettings(indexer)
                query = {
                    'query': fulltext,
                    'default_operator': settings.default_operator,
                    'analyzer': settings.analyzer,
                    'fields': settings.fulltext_search_fields,
                    'lenient': True
                }
                if '"' not in fulltext:
                    query2 = query.copy()
                    query2['query'] = '"{}"'.format(fulltext)
                    yield (Q('simple_query_string', **query) |
                           Q('simple_query_string', **query2))
                else:
                    yield Q('simple_query_string', **query)
