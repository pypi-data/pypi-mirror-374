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

"""PyAMS_content_es.zmi.search module

This module is used to provide components which are used by search engines.
"""

from elasticsearch_dsl import Q, Search
from zope.interface import Interface
from zope.intid import IIntIds
from zope.schema import Bool, TextLine
from zope.schema.vocabulary import getVocabularyRegistry

from pyams_content.root.zmi.search import ISiteRootAdvancedSearchQuery, \
    SiteRootAdvancedSearchForm, SiteRootAdvancedSearchResultsTable, \
    SiteRootAdvancedSearchResultsValues, SiteRootQuickSearchResultsTable, \
    SiteRootQuickSearchResultsValues
from pyams_content.shared.common import IBaseSharedTool, SHARED_CONTENT_TYPES_VOCABULARY
from pyams_content.shared.common.zmi.search import ISharedToolAdvancedSearchQuery, \
    SharedToolAdvancedSearchForm, SharedToolAdvancedSearchResultsTable, \
    SharedToolAdvancedSearchResultsValues, SharedToolQuickSearchResultsTable, \
    SharedToolQuickSearchResultsValues
from pyams_content_es.document import ElasticResultSet
from pyams_content_es.interfaces import IContentIndexerUtility, IQuickSearchSettings, IUserSearchSettings
from pyams_elastic.include import get_client
from pyams_form.field import Fields
from pyams_form.interfaces.form import IFormFields
from pyams_layer.interfaces import IPyAMSLayer
from pyams_sequence.interfaces import ISequentialIntIds
from pyams_sequence.workflow import get_last_version
from pyams_site.interfaces import ISiteRoot
from pyams_table.interfaces import IValues
from pyams_utils.adapter import adapter_config
from pyams_utils.list import unique_iter
from pyams_utils.registry import get_utility
from pyams_workflow.versions import get_last_version_in_state
from pyams_zmi.interfaces import IAdminLayer

__docformat__ = 'restructuredtext'

from pyams_content_es import _


def get_search_params(data):
    """Search params getter"""
    intids = get_utility(IIntIds)
    query = data.get('query')
    if query:
        sequence = get_utility(ISequentialIntIds)
        if query.startswith('+'):
            yield Q('term',
                    reference_id=sequence.get_full_oid(query))
        else:
            indexer = get_utility(IContentIndexerUtility)
            settings = IUserSearchSettings(indexer)
            fulltext = data.get('fulltext', False)
            if fulltext:
                yield (
                    Q('term',
                      reference_id=sequence.get_full_oid(query)) |
                    Q('simple_query_string',
                      query=query,
                      fields=settings.fulltext_search_fields,
                      analyzer=settings.analyzer,
                      default_operator=settings.default_operator,
                      lenient=True))
            else:
                yield (
                    Q('term',
                      reference_id=sequence.get_full_oid(query)) |
                    Q('simple_query_string',
                      query=query,
                      fields=settings.search_fields,
                      analyzer=settings.analyzer,
                      default_operator=settings.default_operator))
    if data.get('owner'):
        yield Q('term',
                owner_id=data['owner'])
    if data.get('status'):
        yield Q('term',
                workflow__status=data['status'])
    if data.get('content_type'):
        yield Q('term',
                content_type=data['content_type'])
    if data.get('data_type'):
        yield Q('term',
                data_type=data['data_type'])
    created_after, created_before = data.get('created', (None, None))
    if created_after:
        yield Q('range',
                workflow__created_date={'gte': created_after})
    if created_before:
        yield Q('range',
                workflow__created_date={'lte': created_before})
    modified_after, modified_before = data.get('modified', (None, None))
    if modified_after:
        yield Q('range',
                workflow__modified_date={'gte': modified_after})
    if modified_before:
        yield Q('range',
                workflow__modified_date={'lte': modified_before})
    if data.get('tags'):
        tags = [intids.register(term) for term in data['tags']]
        yield Q('terms',
                tags=tags)
    if data.get('themes'):
        themes = [intids.register(term) for term in data['themes']]
        yield Q('terms',
                themes__terms=themes)
    if data.get('collections'):
        collections = [intids.register(collection) for collection in data['collections']]
        yield Q('terms',
                collections=collections)


#
# Custom shared tools quick search adapters
#

@adapter_config(required=(IBaseSharedTool, IPyAMSLayer, SharedToolQuickSearchResultsTable),
                provides=IValues)
class EsSharedToolQuickSearchResultsValues(SharedToolQuickSearchResultsValues):
    """Elasticsearch shared tool quick search results values adapter"""

    @property
    def values(self):
        """Table values getter"""
        intids = get_utility(IIntIds)
        query = self.request.params.get('query', '').strip()
        if not query:
            return ()
        sequence = get_utility(ISequentialIntIds)
        query = query.lower()
        if query.startswith('+'):
            params = Q('term',
                       reference_id=sequence.get_full_oid(query))
        else:
            indexer = get_utility(IContentIndexerUtility)
            settings = IQuickSearchSettings(indexer)
            vocabulary = getVocabularyRegistry().get(self.context,
                                                     SHARED_CONTENT_TYPES_VOCABULARY)
            params = (
                Q('term',
                  parent_ids=intids.register(self.context)) &
                Q('terms',
                  content_type=list(vocabulary.by_value.keys())) &
                (Q('term',
                   reference_id=sequence.get_full_oid(query)) |
                 Q('simple_query_string',
                   query=query,
                   fields=settings.search_fields,
                   analyzer=settings.analyzer,
                   default_operator=settings.default_operator)))
        client = get_client(self.request)
        search = Search(using=client.es, index=client.index) \
            .query(params) \
            .source(['internal_id'])
        yield from unique_iter(map(get_last_version, ElasticResultSet(search)))


#
# Custom shared tools advanced search adapters
#

class IEsSharedToolAdvancedSearchQuery(ISharedToolAdvancedSearchQuery):
    """Elasticsearch shared tool advanced search form fields interface"""

    query = TextLine(title=_("Search text"),
                     description=_("Entered text will be search in titles, headers and "
                                   "descriptions"),
                     required=False)

    fulltext = Bool(title=_("Fulltext search"),
                    description=_("Search in fulltext body, including attachments, instead on "
                                  "only searching in titles and headers"))


@adapter_config(required=(Interface, IAdminLayer, SharedToolAdvancedSearchForm),
                provides=IFormFields)
def es_shared_tool_advanced_search_form_fields(context, request, form):
    """Elasticsearch shared tool advanced search form fields getter"""
    return Fields(IEsSharedToolAdvancedSearchQuery).select('query', 'fulltext') + \
        Fields(IEsSharedToolAdvancedSearchQuery).omit('query', 'fulltext',
                                                      'tags', 'themes', 'collections')


@adapter_config(required=(IBaseSharedTool, IPyAMSLayer, SharedToolAdvancedSearchResultsTable),
                provides=IValues)
class EsSharedToolAdvancedSearchResultsValues(SharedToolAdvancedSearchResultsValues):
    """Elasticsearch shared tool advanced search results adapter"""

    def get_params(self, data):
        """Extract Elasticsearch query params from incoming request"""
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = Q('term',
                   parent_ids=intids.register(self.context)) & \
            Q('terms',
              content_type=list(vocabulary.by_value.keys()))
        for param in get_search_params(data):
            params &= param
        return params

    @property
    def values(self):
        """Query values getter"""
        form = SharedToolAdvancedSearchForm(self.context, self.request)
        form.update()
        data, _errors = form.extract_data()
        params = self.get_params(data)
        client = get_client(self.request)
        search = Search(using=client.es, index=client.index) \
            .query(params) \
            .source(['internal_id'])
        sort_order = [{
            'workflow.modified_date': {
                'unmapped_type': 'date',
                'order': 'desc'
            }
        }]
        if data.get('query'):
            sort_order.insert(0, {
                '_score': {
                    'order': 'desc'
                }
            })
        search = search.sort(*sort_order)
        if data.get('status'):
            yield from unique_iter(map(get_last_version_in_state, ElasticResultSet(search)))
        else:
            yield from unique_iter(map(get_last_version, ElasticResultSet(search)))


#
# Custom site root quick search results adapters
#

@adapter_config(required=(ISiteRoot, IPyAMSLayer, SiteRootQuickSearchResultsTable),
                provides=IValues)
class EsSiteRootQuickSearchResultsValues(SiteRootQuickSearchResultsValues):
    """Elasticsearch site root quick search results table values adapter"""

    @property
    def values(self):
        """Table values getter"""
        query = self.request.params.get('query', '').strip()
        if not query:
            return ()
        sequence = get_utility(ISequentialIntIds)
        query = query.lower()
        if query.startswith('+'):
            params = Q('term',
                       reference_id=sequence.get_full_oid(query))
        else:
            vocabulary = getVocabularyRegistry().get(self.context,
                                                     SHARED_CONTENT_TYPES_VOCABULARY)
            indexer = get_utility(IContentIndexerUtility)
            settings = IQuickSearchSettings(indexer)
            params = (
                Q('terms',
                  content_type=list(vocabulary.by_value.keys())) &
                (Q('term',
                   reference_id=sequence.get_full_oid(query)) |
                 Q('simple_query_string',
                   query=query,
                   fields=settings.search_fields,
                   analyzer=settings.analyzer,
                   default_operator=settings.default_operator)))
        client = get_client(self.request)
        search = Search(using=client.es, index=client.index) \
            .query(params) \
            .source(['internal_id'])
        yield from unique_iter(map(get_last_version, ElasticResultSet(search)))


#
# Custom site root advanced search adapters
#

class IEsSiteRootAdvancedSearchQuery(ISiteRootAdvancedSearchQuery):
    """Elasticsearch site root advanced search form fields interfaces"""

    query = TextLine(title=_("Search text"),
                     description=_("Entered text will be search in titles, headers and "
                                   "descriptions"),
                     required=False)

    fulltext = Bool(title=_("Fulltext search"),
                    description=_("Search in fulltext body, including attachments, instead on "
                                  "only searching in titles and headers"))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootAdvancedSearchForm),
                provides=IFormFields)
def es_site_root_advanced_search_form_fields(context, request, form):
    """Elasticsearch site root advanced search form fields getter"""
    return Fields(IEsSiteRootAdvancedSearchQuery).select('query', 'fulltext') + \
        Fields(IEsSiteRootAdvancedSearchQuery).omit('query', 'fulltext',
                                                    'tags', 'themes', 'collections')


@adapter_config(required=(ISiteRoot, IPyAMSLayer, SiteRootAdvancedSearchResultsTable),
                provides=IValues)
class EsSiteRootAdvancedSearchResultsValues(SiteRootAdvancedSearchResultsValues):
    """Elasticsearch site root advanced search results adapter"""

    def get_params(self, data):
        """Extract Elasticsearch query params from incoming request"""
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = Q('terms',
                   content_type=list(vocabulary.by_value.keys()))
        for param in get_search_params(data):
            params &= param
        return params

    @property
    def values(self):
        form = SiteRootAdvancedSearchForm(self.context, self.request)
        form.update()
        data, _errors = form.extract_data()
        params = self.get_params(data)
        client = get_client(self.request)
        search = Search(using=client.es, index=client.index) \
            .query(params) \
            .source(['internal_id'])
        sort_order = [{
            'workflow.modified_date': {
                'unmapped_type': 'date',
                'order': 'desc'
            }
        }]
        if data.get('query'):
            sort_order.insert(0, {
                '_score': {
                    'order': 'desc'
                }
            })
        search = search.sort(*sort_order)
        yield from unique_iter(map(get_last_version, ElasticResultSet(search)))
