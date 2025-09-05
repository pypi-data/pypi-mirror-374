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

"""PyAMS_content_es.component.workflow module

This module defines adapters which are used to handle indexation of
workflow status information.
"""

__docformat__ = 'restructuredtext'

from pyramid.events import subscriber
from transaction.interfaces import ITransactionManager
from zope.dublincore.interfaces import IZopeDublinCore
from zope.intid import IIntIds

from pyams_content_es.document import INDEXED_DOCUMENTS_EXTENSION
from pyams_content_es.interfaces import IContentIndexerUtility, IDocumentIndexInfo, \
    IDocumentIndexTarget
from pyams_utils.adapter import adapter_config
from pyams_utils.registry import get_utility, query_utility
from pyams_workflow.interfaces import IWorkflowInfo, IWorkflowPublicationInfo, \
    IWorkflowPublicationSupport, IWorkflowState, IWorkflowTransitionEvent


@adapter_config(name='workflow',
                required=IWorkflowPublicationSupport,
                provides=IDocumentIndexInfo)
def workflow_managed_index_info(content):
    """Workflow managed content index info"""
    result = {}
    dc_info = IZopeDublinCore(content, None)
    if dc_info is not None:
        result.update({
            'created_date': dc_info.created,
            'modified_date': dc_info.modified
        })
    workflow_info = IWorkflowInfo(content, None)
    if workflow_info is not None:
        result.update({
            'name': workflow_info.name
        })
    workflow_pub_info = IWorkflowPublicationInfo(content, None)
    if workflow_pub_info is not None:
        result.update({
            'publication_date': workflow_pub_info.publication_date,
            'effective_date': workflow_pub_info.publication_effective_date,
            'push_end_date': workflow_pub_info.push_end_date,
            'expiration_date': workflow_pub_info.publication_expiration_date,
            'first_publication_date': workflow_pub_info.first_publication_date,
            'content_publication_date': workflow_pub_info.content_publication_date,
            'visible_publication_date': workflow_pub_info.visible_publication_date
        })
    workflow_state = IWorkflowState(content, None)
    if workflow_state is not None:
        result.update({
            'status': workflow_state.state,
            'principal': workflow_state.state_principal,
            'date': workflow_state.state_date,
        })
    return {
        'workflow': result
    }


@subscriber(IWorkflowTransitionEvent, context_selector=IDocumentIndexTarget)
def handle_workflow_transition(event):
    """Handle workflow transition

    When a workflow transition occurs, just update document workflow information
    instead of the whole document.
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
        indexer.update_document(document, ['workflow'])
