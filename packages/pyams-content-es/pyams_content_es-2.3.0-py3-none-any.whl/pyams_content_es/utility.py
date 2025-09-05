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

"""PyAMS_content_es.utility module

"""

__docformat__ = 'restructuredtext'

from persistent import Persistent
from zope.container.contained import Contained
from zope.intid import IIntIds
from zope.schema.fieldproperty import FieldProperty

from pyams_content_es.interfaces import IContentIndexerUtility, INDEXER_AUTH_KEY, \
    INDEXER_HANDLER_KEY, IQuickSearchSettings, IUserSearchSettings, LOGGER, QUICK_SEARCH_SETTINGS_KEY, \
    USER_SEARCH_SETTINGS_KEY
from pyams_utils.adapter import adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config
from pyams_utils.registry import get_pyramid_registry, get_utility
from pyams_utils.transaction import TransactionClient, transactional
from pyams_zmq.socket import zmq_response, zmq_socket


class IndexUpdateHandler(TransactionClient):
    """Content indexer transactional client class"""

    def __init__(self, indexer):
        super().__init__()
        self.indexer = indexer

    @transactional
    def update_index(self, action, document, **kwargs):
        """Call action on Elasticsearch document indexer"""
        socket = self.indexer.get_socket()
        if socket is None:
            return [501, "No socket handler defined in configuration file"]
        if action in ('index_document', 'update_document'):
            intids = get_utility(IIntIds)
            document = intids.queryId(document)
        settings = {
            'zodb_name': self.indexer.zodb_name,
            'document': document
        }
        settings.update(kwargs)
        LOGGER.debug(f"Sending JSON message: action={action}, {settings}")
        socket.send_json([action, settings])
        return zmq_response(socket)


@factory_config(IContentIndexerUtility)
class ContentIndexerUtility(Persistent, Contained):
    """Elasticsearch content index utility"""

    zodb_name = FieldProperty(IContentIndexerUtility['zodb_name'])

    @staticmethod
    def get_socket():
        """Open ØMQ socket"""
        registry = get_pyramid_registry()
        handler = registry.settings.get(INDEXER_HANDLER_KEY, False)
        if handler:
            return zmq_socket(handler, auth=registry.settings.get(INDEXER_AUTH_KEY))
        return None

    def test_process(self):
        """Send test request to document indexer process"""
        socket = self.get_socket()
        if socket is None:
            return [501, "No socket handler defined in configuration file"]
        socket.send_json(['test', {}])
        return zmq_response(socket)

    def index_document(self, document):
        """Add or update document to Elasticsearch index"""
        handler = IndexUpdateHandler(self)
        return handler.update_index('index_document', document)

    def update_document(self, document, attrs):
        """Update document attributes in Elasticsearch index"""
        handler = IndexUpdateHandler(self)
        return handler.update_index('update_document', document, attrs=attrs)

    def unindex_document(self, document_oid):
        """Remove document from Elasticsearch index"""
        handler = IndexUpdateHandler(self)
        return handler.update_index('unindex_document', document_oid)


#
# Backoffice quick search settings
#

@factory_config(IQuickSearchSettings)
class QuickSearchSettings(Persistent, Contained):
    """Quick search settings persistent class"""

    analyzer = FieldProperty(IQuickSearchSettings['analyzer'])
    search_fields = FieldProperty(IQuickSearchSettings['search_fields'])
    default_operator = FieldProperty(IQuickSearchSettings['default_operator'])


@adapter_config(required=IContentIndexerUtility,
                provides=IQuickSearchSettings)
def content_indexer_quick_search_settings(context):
    """Content indexer quick search settings"""
    return get_annotation_adapter(context, QUICK_SEARCH_SETTINGS_KEY,
                                  IQuickSearchSettings)


#
# Default user search settings
#

@factory_config(IUserSearchSettings)
class UserSearchSettings(Persistent, Contained):
    """User search settings persistent class"""

    analyzer = FieldProperty(IUserSearchSettings['analyzer'])
    search_fields = FieldProperty(IUserSearchSettings['search_fields'])
    fulltext_search_fields = FieldProperty(IUserSearchSettings['fulltext_search_fields'])
    default_operator = FieldProperty(IUserSearchSettings['default_operator'])


@adapter_config(required=IContentIndexerUtility,
                provides=IUserSearchSettings)
def content_indexer_user_search_settings(context):
    """Content indexer user search settings"""
    return get_annotation_adapter(context, USER_SEARCH_SETTINGS_KEY,
                                  IUserSearchSettings)
