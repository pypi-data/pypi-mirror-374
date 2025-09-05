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

"""PyAMS_*** module

"""

from datetime import datetime, timezone

from elasticsearch_dsl import Search
from pyramid.events import subscriber
from transaction.interfaces import ITransactionManager
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import classImplements
from zope.intid import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectModifiedEvent, IObjectRemovedEvent

from pyams_catalog.query import CatalogResultSet
from pyams_content.shared.common import WfSharedContent
from pyams_content.shared.common.interfaces import IPreventSharedContentUpdateSubscribers, ISharedTool, \
    IWfSharedContent, IWfSharedContentRoles
from pyams_content.shared.common.interfaces.types import IWfTypedSharedContent
from pyams_content_es.interfaces import IContentIndexerUtility, IDocumentIndexInfo, IDocumentIndexTarget
from pyams_elastic.include import get_client
from pyams_elastic.mixin import ESField, ESKeyword, ESMapping, ESText, ElasticMixin
from pyams_i18n.interfaces import II18n
from pyams_sequence.interfaces import ISequentialIdInfo
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.traversing import IPathElements
from pyams_utils.registry import get_pyramid_registry, get_utility, query_utility
from pyams_utils.request import query_request
from pyams_utils.traversing import get_parent
from pyams_workflow.interfaces import IWorkflowState

__docformat__ = 'restructuredtext'


def get_internal_id(doc):
    """Internal ID getter"""
    return doc.internal_id


def get_elastic_search(request, params, index=None):
    """Create Elasticsearch query from given params"""
    client = get_client(request)
    return Search(using=client.es,
                  index=index or client.index) \
        .query(params) \
        .source(['internal_id'])


def ElasticResultSet(search, length=999):
    """Elasticsearch documents results set

    Returns an iterator on documents from an Elasticsearch query
    containing documents internal IDs.
    """
    return CatalogResultSet(map(get_internal_id, search[:length]))


class ElasticDocumentMixin(ElasticMixin):
    """Elasticsearch document mixin class"""

    @property
    def id(self):
        """Document ID getter"""
        oid = ISequentialIdInfo(self).hex_oid
        state = IWorkflowState(self, None)
        if state is None:
            return oid
        return f'{oid}.{state.version_id}'

    @property
    def timestamp(self):
        """Timestamp getter"""
        dc = IZopeDublinCore(self, None)
        if dc is None:
            return datetime.now(timezone.utc)
        return dc.modified

    @property
    def internal_id(self):
        """Internal ID getter"""
        intids = get_utility(IIntIds)
        return intids.register(self)

    @property
    def reference_id(self):
        """Reference ID getter"""
        return ISequentialIdInfo(self).hex_oid

    @property
    def owner_id(self):
        """Owner ID getter"""
        return list(IWfSharedContentRoles(self).owner or ())

    @property
    def contributor_id(self):
        """Contributor IDs getter"""
        return list(IWfSharedContentRoles(self).contributors or ())

    @property
    def facet_label(self):
        """Facet label getter"""
        request = query_request()
        if IWfTypedSharedContent.providedBy(self):
            data_type = self.get_data_type()
            if data_type is not None:
                i18n = II18n(data_type)
                return i18n.query_attributes_in_order(('facets_label', 'label'),
                                                      request=request)
        shared_tool = get_parent(self, ISharedTool)
        if shared_tool is not None:
            i18n = II18n(shared_tool)
            return i18n.query_attributes_in_order(('facets_label', 'label', 'title'),
                                                  request=request)
        return None

    @property
    def facet_type_label(self):
        """Facet-type label getter"""
        request = query_request()
        if IWfTypedSharedContent.providedBy(self):
            data_type = self.get_data_type()
            if data_type is not None:
                i18n = II18n(data_type)
                return i18n.query_attributes_in_order(('facets_type_label', 'label'),
                                                      request=request)
        shared_tool = get_parent(self, ISharedTool)
        if shared_tool is not None:
            i18n = II18n(shared_tool)
            return i18n.query_attributes_in_order(('facets_type_label', 'label', 'title'),
                                                  request=request)
        return None

    def elastic_mapping(self):
        """Elasticsearch mapping getter"""
        return IDocumentIndexInfo(self)

    def elastic_document(self):
        document_info = super().elastic_document()
        registry = get_pyramid_registry()
        for name, index_info in registry.getAdapters((self,), IDocumentIndexInfo):
            if not name:
                continue
            if 'body' in index_info:
                body = document_info.get('body', {})
                for lang, body_info in index_info['body'].items():
                    body[lang] = f"{body.get(lang, '')}\n{body_info}"
                document_info['body'] = body
            else:
                document_info.update(index_info)
        return document_info


WfSharedContent.__bases__ += (ElasticDocumentMixin,)
classImplements(WfSharedContent, IDocumentIndexTarget)


@adapter_config(required=IWfSharedContent,
                provides=IDocumentIndexInfo)
def shared_content_index_info(content):
    """Shared content index info"""
    return ESMapping(properties=ESMapping(ESField('@timestamp', attr='timestamp'),
                                          ESKeyword('internal_id'),
                                          ESKeyword('reference_id'),
                                          ESKeyword('owner_id'),
                                          ESKeyword('contributor_id'),
                                          ESKeyword('content_type'),
                                          ESKeyword('facet_label'),
                                          ESKeyword('facet_type_label'),
                                          ESText('title'),
                                          ESText('short_name'),
                                          ESText('header'),
                                          ESText('description'),
                                          ESText('keywords')))


@adapter_config(required=IWfTypedSharedContent,
                provides=IDocumentIndexInfo)
def typed_shared_content_index_info(content):
    """Typed shared content index info"""
    return ESMapping(properties=ESMapping(ESField('@timestamp', attr='timestamp'),
                                          ESKeyword('internal_id'),
                                          ESKeyword('reference_id'),
                                          ESKeyword('owner_id'),
                                          ESKeyword('contributor_id'),
                                          ESKeyword('content_type'),
                                          ESKeyword('data_type'),
                                          ESKeyword('facet_label'),
                                          ESKeyword('facet_type_label'),
                                          ESText('title'),
                                          ESText('short_name'),
                                          ESText('header'),
                                          ESText('description'),
                                          ESText('keywords')))


@adapter_config(name='path',
                required=IWfSharedContent,
                provides=IDocumentIndexInfo)
def shared_content_path_index_info(content):
    """Shared content path index info"""
    return {
        'parent_ids': IPathElements(content).parents
    }


@subscriber(IObjectAddedEvent, context_selector=IDocumentIndexTarget)
def handle_added_document(event):
    """Handle added document"""
    indexer = query_utility(IContentIndexerUtility)
    if indexer is None:
        return
    indexer.index_document(event.object)


INDEXED_DOCUMENTS_EXTENSION = 'pyams_content_es.indexed_documents'


@subscriber(IObjectModifiedEvent, context_selector=IDocumentIndexTarget)
def handle_modified_document(event):
    """Handle modified document

    We use transaction annotations to avoid several indexations of the same
    document during a single transaction...
    """
    indexer = query_utility(IContentIndexerUtility)
    if indexer is None:
        return
    intids = get_utility(IIntIds)
    document = event.object
    document_id = intids.register(document)
    transaction = ITransactionManager(document).get()
    documents = transaction.extension.get(INDEXED_DOCUMENTS_EXTENSION) or set()
    if document_id not in documents:
        documents.add(document_id)
        transaction.extension[INDEXED_DOCUMENTS_EXTENSION] = documents
        indexer.index_document(document)


@subscriber(IObjectRemovedEvent, context_selector=IDocumentIndexTarget)
def handle_removed_document(event):
    """Handle removed document"""
    indexer = query_utility(IContentIndexerUtility)
    if indexer is None:
        return
    document = event.object
    oid = ISequentialIdInfo(document).hex_oid
    wf_state = IWorkflowState(document, None)
    document_oid = f'{oid}.{wf_state.version_id}' if wf_state else oid
    indexer.unindex_document(document_oid)


@subscriber(IObjectAddedEvent)
@subscriber(IObjectModifiedEvent)
@subscriber(IObjectRemovedEvent)
def handle_modified_inner_content(event):
    """Handle modified shared object inner content

    This generic subscriber is used to update index on any content modification.
    """
    source = event.object
    if IWfSharedContent.providedBy(source):
        return
    handler = IPreventSharedContentUpdateSubscribers(source, None)
    if handler is not None:
        return
    content = get_parent(event.object, IWfSharedContent, allow_context=False)
    if content is None:
        return
    handle_modified_document(ObjectModifiedEvent(content))
