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

__docformat__ = 'restructuredtext'

from elasticsearch_dsl import Q
from zope.intid import IIntIds
from zope.schema.vocabulary import getVocabularyRegistry

from pyams_content.root.zmi.dashboard import SiteRootArchivedContentsTable, \
    SiteRootArchivedContentsValues, SiteRootDashboardManagerWaitingTable, \
    SiteRootDashboardManagerWaitingValues, SiteRootDashboardOwnerModifiedTable, \
    SiteRootDashboardOwnerModifiedValues, SiteRootDashboardOwnerWaitingTable, \
    SiteRootDashboardOwnerWaitingValues, SiteRootLastModificationsTable, \
    SiteRootLastModificationsValues, SiteRootLastPublicationsTable, \
    SiteRootLastPublicationsValues, SiteRootPreparationsTable, SiteRootPreparationsValues, \
    SiteRootPublicationsTable, SiteRootPublicationsValues, SiteRootRetiredContentsTable, \
    SiteRootRetiredContentsValues, SiteRootSubmissionsTable, SiteRootSubmissionsValues
from pyams_content.shared.common.interfaces import IBaseSharedTool, SHARED_CONTENT_TYPES_VOCABULARY
from pyams_content.shared.common.zmi.dashboard import SharedToolArchivedContentsTable, \
    SharedToolArchivedContentsValues, SharedToolDashboardManagerWaitingTable, \
    SharedToolDashboardManagerWaitingValues, SharedToolDashboardOwnerWaitingTable, \
    SharedToolDashboardOwnerWaitingValues, SharedToolLastModificationsTable, \
    SharedToolLastModificationsValues, SharedToolLastPublicationsTable, \
    SharedToolLastPublicationsValues, SharedToolPreparationsTable, SharedToolPreparationsValues, \
    SharedToolPublicationsTable, SharedToolPublicationsValues, SharedToolRetiredContentsTable, \
    SharedToolRetiredContentsValues, SharedToolSubmissionsTable, SharedToolSubmissionsValues
from pyams_content_es.document import ElasticResultSet, get_elastic_search
from pyams_site.interfaces import ISiteRoot
from pyams_table.interfaces import IValues
from pyams_utils.adapter import adapter_config
from pyams_utils.list import unique_iter
from pyams_utils.registry import get_all_utilities_registered_for, get_utility
from pyams_workflow.interfaces import IWorkflow
from pyams_workflow.versions import get_last_version_in_state
from pyams_zmi.interfaces import IAdminLayer


MODIFIED_DATE_FIELD = 'workflow.modified_date'


#
# Elasticsearch shared tools dashboards adapters
#

@adapter_config(required=(IBaseSharedTool, IAdminLayer, SharedToolDashboardManagerWaitingTable),
                provides=IValues)
class EsSharedToolDashboardManagerWaitingValues(SharedToolDashboardManagerWaitingValues):
    """Elasticsearch shared tool dashboard manager waiting values getter"""

    @property
    def values(self):
        """Table values adapter"""
        intids = get_utility(IIntIds)
        workflow = IWorkflow(self.context)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = (
            Q('term', parent_ids=intids.register(self.context)) &
            Q('terms', content_type=list(vocabulary.by_value.keys())) &
            Q('terms', workflow__status=list(workflow.waiting_states)))
        search = get_elastic_search(self.request, params)
        yield from filter(
            self.check_access,
            unique_iter(map(get_last_version_in_state, ElasticResultSet(search))))


@adapter_config(required=(IBaseSharedTool, IAdminLayer, SharedToolDashboardOwnerWaitingTable),
                provides=IValues)
class EsSharedToolDashboardOwnerWaitingValues(SharedToolDashboardOwnerWaitingValues):
    """Elasticsearch shared tool dashboard waiting owned contents values adapter"""

    @property
    def values(self):
        """Table values getter"""
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        workflow = IWorkflow(self.context)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = (
            Q('term', parent_ids=intids.register(self.context)) &
            Q('terms', content_type=list(vocabulary.by_value.keys())) &
            Q('terms', workflow__status=list(workflow.waiting_states)) &
            Q('term', workflow__principal=principal_id))
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(map(get_last_version_in_state, ElasticResultSet(search)))


@adapter_config(required=(IBaseSharedTool, IAdminLayer, SharedToolPreparationsTable),
                provides=IValues)
class EsSharedToolPreparationsValues(SharedToolPreparationsValues):
    """Elasticsearch shared tool preparations values adapter"""

    @property
    def values(self):
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        workflow = IWorkflow(self.context)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = (
            Q('term', parent_ids=intids.register(self.context)) &
            Q('terms', content_type=list(vocabulary.by_value.keys())) &
            (Q('term', owner_id=principal_id) |
             Q('term', contributor_id=principal_id)) &
            Q('term', workflow__status=workflow.initial_state)
        )
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(IBaseSharedTool, IAdminLayer, SharedToolSubmissionsTable),
                provides=IValues)
class EsSharedToolSubmissionsValues(SharedToolSubmissionsValues):
    """Elasticsearch shared tool submissions values adapter"""

    @property
    def values(self):
        context = self.context
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        workflow = IWorkflow(context)
        vocabulary = getVocabularyRegistry().get(context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = (
            Q('term', parent_ids=intids.register(self.context)) &
            Q('terms', content_type=list(vocabulary.by_value.keys())) &
            (Q('term', owner_id=principal_id) |
             Q('term', contributor_id=principal_id)) &
            Q('terms', workflow__status=list(workflow.waiting_states))
        )
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(IBaseSharedTool, IAdminLayer, SharedToolPublicationsTable),
                provides=IValues)
class EsSharedToolPublicationsValues(SharedToolPublicationsValues):
    """Elasticsearch shared tool publications values adapter"""

    @property
    def values(self):
        context = self.context
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        workflow = get_utility(IWorkflow, name=context.shared_content_workflow)
        vocabulary = getVocabularyRegistry().get(context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = (
            Q('term', parent_ids=intids.register(self.context)) &
            Q('terms', content_type=list(vocabulary.by_value.keys())) &
            (Q('term', owner_id=principal_id) |
             Q('term', contributor_id=principal_id)) &
            Q('terms', workflow__status=list(workflow.published_states))
        )
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(IBaseSharedTool, IAdminLayer, SharedToolRetiredContentsTable),
                provides=IValues)
class EsSharedToolRetiredContentsValues(SharedToolRetiredContentsValues):
    """Elasticsearch shared tool retired contents values adapter"""

    @property
    def values(self):
        context = self.context
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        workflow = get_utility(IWorkflow, name=context.shared_content_workflow)
        vocabulary = getVocabularyRegistry().get(context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = (
            Q('term', parent_ids=intids.register(self.context)) &
            Q('terms', content_type=list(vocabulary.by_value.keys())) &
            (Q('term', owner_id=principal_id) |
             Q('term', contributor_id=principal_id)) &
            Q('terms', workflow__status=list(workflow.retired_states))
        )
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(IBaseSharedTool, IAdminLayer, SharedToolArchivedContentsTable),
                provides=IValues)
class EsSharedToolArchivedContentsValues(SharedToolArchivedContentsValues):
    """Elasticsearch shared tool archived contents values adapter"""

    @property
    def values(self):
        context = self.context
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        workflow = get_utility(IWorkflow, name=context.shared_content_workflow)
        vocabulary = getVocabularyRegistry().get(context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = (
            Q('term', parent_ids=intids.register(self.context)) &
            Q('terms', content_type=list(vocabulary.by_value.keys())) &
            (Q('term', owner_id=principal_id) |
             Q('term', contributor_id=principal_id)) &
            Q('terms', workflow__status=list(workflow.archived_states))
        )
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(IBaseSharedTool, IAdminLayer, SharedToolLastPublicationsTable),
                provides=IValues)
class EsSharedToolLastPublicationsValues(SharedToolLastPublicationsValues):
    """Elasticsearch shared tool publications values adapter"""

    @property
    def values(self):
        intids = get_utility(IIntIds)
        workflow = get_utility(IWorkflow, name=self.context.shared_content_workflow)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = (
            Q('term', parent_ids=intids.register(self.context)) &
            Q('terms', content_type=list(vocabulary.by_value.keys())) &
            Q('terms', workflow__status=list(workflow.published_states))
        )
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search, 50))


@adapter_config(required=(IBaseSharedTool, IAdminLayer, SharedToolLastModificationsTable),
                provides=IValues)
class EsSharedToolLastModificationsValues(SharedToolLastModificationsValues):
    """Elasticsearch shared tool modifications values adapter"""

    @property
    def values(self):
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = (
            Q('term', parent_ids=intids.register(self.context)) &
            Q('terms', content_type=list(vocabulary.by_value.keys()))
        )
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search, 50))


#
# Elasticsearch site root dashboards adapters
#

@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootDashboardManagerWaitingTable),
                provides=IValues)
class EsSiteRootDashboardManagerWaitingValues(SiteRootDashboardManagerWaitingValues):
    """Elasticsearch site root dashboard waiting values adapter"""

    @property
    def values(self):
        """Table values getter"""
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = None
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            workflow = IWorkflow(tool)
            query = (
                Q('term', parent_ids=intids.register(tool)) &
                Q('terms', content_type=list(vocabulary.by_value.keys())) &
                Q('terms', workflow__status=list(workflow.waiting_states))
            )
            params = params | query if params else query
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from filter(
            self.check_access,
            unique_iter(map(get_last_version_in_state, ElasticResultSet(search))))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootDashboardOwnerWaitingTable),
                provides=IValues)
class EsSiteRootDashboardOwnerWaitingValues(SiteRootDashboardOwnerWaitingValues):
    """Elasticsearch site root dashboard waiting owned contents values adapter"""

    @property
    def values(self):
        """Table values getter"""
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = None
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            workflow = IWorkflow(tool)
            query = (
                Q('term', parent_ids=intids.register(tool)) &
                Q('terms', content_type=list(vocabulary.by_value.keys())) &
                Q('terms', workflow__status=list(workflow.waiting_states)) &
                Q('term', workflow__principal=principal_id)
            )
            params = params | query if params else query
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(map(get_last_version_in_state, ElasticResultSet(search)))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootDashboardOwnerModifiedTable),
                provides=IValues)
class EsSiteRootDashboardOwnerModifiedValues(SiteRootDashboardOwnerModifiedValues):
    """Elasticsearch site root dashboard owner modified adapter"""

    @property
    def values(self):
        """Table values getter"""
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = None
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            query = (
                Q('term', parent_ids=intids.register(tool)) &
                Q('terms', content_type=list(vocabulary.by_value.keys())) &
                (Q('term', owner_id=principal_id) |
                 Q('term', contributor_id=principal_id))
            )
            params = params | query if params else query
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(map(get_last_version_in_state, ElasticResultSet(search, 50)))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootPreparationsTable),
                provides=IValues)
class EsSiteRootPreparationsValues(SiteRootPreparationsValues):
    """Elasticsearch site root preparations values adapter"""

    @property
    def values(self):
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = None
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            workflow = IWorkflow(tool)
            query = (
                Q('term', parent_ids=intids.register(tool)) &
                Q('terms', content_type=list(vocabulary.by_value.keys())) &
                (Q('term', owner_id=principal_id) |
                 Q('term', contributor_id=principal_id)) &
                Q('term', workflow__status=workflow.initial_state)
            )
            params = params | query if params else query
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootSubmissionsTable),
                provides=IValues)
class EsSiteRootSubmissionsValues(SiteRootSubmissionsValues):
    """Elasticsearch site root submissions values adapter"""

    @property
    def values(self):
        context = self.context
        principal_id = self.request.principal.id
        intids  =get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = None
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            workflow = IWorkflow(tool)
            query = (
                Q('term', parent_ids=intids.register(tool)) &
                Q('terms', content_type=list(vocabulary.by_value.keys())) &
                (Q('term', owner_id=principal_id) |
                 Q('term', contributor_id=principal_id)) &
                Q('terms', workflow__status=list(workflow.waiting_states))
            )
            params = params | query if params else query
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootPublicationsTable),
                provides=IValues)
class EsSiteRootPublicationsValues(SiteRootPublicationsValues):
    """Elasticsearch site root publications values adapter"""

    @property
    def values(self):
        context = self.context
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = None
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            workflow = IWorkflow(tool)
            query = (
                Q('term', parent_ids=intids.register(tool)) &
                Q('terms', content_type=list(vocabulary.by_value.keys())) &
                (Q('term', owner_id=principal_id) |
                 Q('term', contributor_id=principal_id)) &
                Q('terms', workflow__status=list(workflow.published_states))
            )
            params = params | query if params else query
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootRetiredContentsTable),
                provides=IValues)
class EsSiteRootRetiredContentsValues(SiteRootRetiredContentsValues):
    """Elasticsearch site root retired contents values adapter"""

    @property
    def values(self):
        context = self.context
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = None
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            workflow = IWorkflow(tool)
            query = (
                Q('term', parent_ids=intids.register(tool)) &
                Q('terms', content_type=list(vocabulary.by_value.keys())) &
                (Q('term', owner_id=principal_id) |
                 Q('term', contributor_id=principal_id)) &
                Q('terms', workflow__status=list(workflow.retired_states))
            )
            params = params | query if params else query
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootArchivedContentsTable),
                provides=IValues)
class EsSiteRootArchivedContentsValues(SiteRootArchivedContentsValues):
    """Elasticsearch site root archived contents values adapter"""

    @property
    def values(self):
        context = self.context
        principal_id = self.request.principal.id
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = None
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            workflow = IWorkflow(tool)
            query = (
                Q('term', parent_ids=intids.register(tool)) &
                Q('terms', content_type=list(vocabulary.by_value.keys())) &
                (Q('term', owner_id=principal_id) |
                 Q('term', contributor_id=principal_id)) &
                Q('terms', workflow__status=list(workflow.archived_states))
            )
            params = params | query if params else query
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootLastPublicationsTable),
                provides=IValues)
class EsSiteRootLastPublicationsValues(SiteRootLastPublicationsValues):
    """Elasticsearch site root publications values adapter"""

    @property
    def values(self):
        intids = get_utility(IIntIds)
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = None
        for tool in get_all_utilities_registered_for(IBaseSharedTool):
            workflow = IWorkflow(tool)
            query = (
                Q('term', parent_ids=intids.register(tool)) &
                Q('terms', content_type=list(vocabulary.by_value.keys())) &
                Q('terms', workflow__status=list(workflow.published_states))
            )
            params = params | query if params else query
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search, 50))


@adapter_config(required=(ISiteRoot, IAdminLayer, SiteRootLastModificationsTable),
                provides=IValues)
class EsSiteRootLastModificationsValues(SiteRootLastModificationsValues):
    """Elasticsearch site root modifications values adapter"""

    @property
    def values(self):
        vocabulary = getVocabularyRegistry().get(self.context, SHARED_CONTENT_TYPES_VOCABULARY)
        params = Q('terms', content_type=list(vocabulary.by_value.keys()))
        search = get_elastic_search(self.request, params) \
            .sort({
                MODIFIED_DATE_FIELD: {
                    'unmapped_type': 'date',
                    'order': 'desc'
                }
            })
        yield from unique_iter(ElasticResultSet(search, 50))
