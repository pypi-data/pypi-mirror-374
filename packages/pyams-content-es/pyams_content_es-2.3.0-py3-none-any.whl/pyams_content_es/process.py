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

"""PyAMS_content_es.process module

This module defines PyAMS_content indexing process.
"""
from multiprocessing import Process

from pprint import pformat
from pyramid.threadlocal import RequestContext
from threading import Thread
from transaction.interfaces import ITransactionManager
from zope.interface import implementer
from zope.intid import IIntIds

from pyams_content_es.interfaces import IContentIndexerProcess, LOGGER
from pyams_elastic.include import client_from_config
from pyams_site.interfaces import PYAMS_APPLICATION_DEFAULT_NAME, PYAMS_APPLICATION_SETTINGS_KEY
from pyams_utils.registry import get_pyramid_registry, get_utility, set_local_registry
from pyams_utils.request import check_request
from pyams_utils.transaction import COMMITTED_STATUS
from pyams_utils.zodb import ZODBConnection
from pyams_zmq.handler import ZMQMessageHandler
from pyams_zmq.process import ZMQProcess


__docformat__ = 'restructuredtext'


class BaseIndexUpdaterProcess(Process):
    """Base Elasticsearch index updater process"""

    def __init__(self, registry, settings, group=None, target=None, name=None, *args, **kwargs):
        super().__init__(group, target, name, *args, **kwargs)
        self.registry = registry
        self.settings = settings

    def run(self):
        """Index update process"""
        LOGGER.debug("Starting Elastincsearch index updater process...")
        # check settings
        settings = self.settings
        LOGGER.debug(f"Checking parameters: {settings}")
        document_id = settings.pop('document', None)
        if not document_id:
            LOGGER.warning("Elasticsearch index updater: missing document ID!")
            return
        # loading components registry
        registry = self.registry
        LOGGER.debug(f"Getting Pyramid registry: {registry!r}")
        # get ES client
        es_client = client_from_config(registry.settings)
        if es_client is None:
            LOGGER.warning("Missing Elasticsearch client configuration!")
            return
        # create new request
        request = check_request()
        request.registry = registry
        LOGGER.debug(f"Creating new request {request!r}")
        with RequestContext(request):
            # open ZODB connection
            LOGGER.debug("Opening ZODB connection...")
            zodb_name = settings.pop('zodb_name', '')
            with ZODBConnection(zodb_name) as root:
                LOGGER.debug(f"Getting database root {root!r}")
                application_name = registry.settings.get(PYAMS_APPLICATION_SETTINGS_KEY,
                                                         PYAMS_APPLICATION_DEFAULT_NAME)
                application = root.get(application_name)
                LOGGER.debug(f"Loaded application {application!r} "
                             f"with name {application_name}")
                if application is not None:
                    # set local registry
                    sm = application.getSiteManager()
                    set_local_registry(sm)
                    LOGGER.debug(f"Setting local registry {sm!r}")
                    self.update_index(es_client, document_id, **settings)

    def update_index(self, client, document_id, **kwargs):
        """Update Elasticsearch index"""
        raise NotImplementedError("Index updater process must implement update_index method!")


class DocumentIndexProcess(BaseIndexUpdaterProcess):
    """Document indexer process"""

    def update_index(self, client, document_id, **kwargs):
        """Add document to Elasticsearch index

        Document ID must be provided as an internal reference ID, as provided
        by IntIds utility.
        """
        # search document
        intids = get_utility(IIntIds)
        document = intids.queryObject(document_id)
        if document is None:
            LOGGER.warning(f"Can't find requested document {document_id}!")
            return
        # index document
        LOGGER.debug(f"Starting indexing for {document!r}")
        manager = ITransactionManager(document, None)
        try:
            for attempt in manager.attempts():
                with attempt as t:
                    client.index_object(document)
                if t.status == COMMITTED_STATUS:
                    break
        finally:
            if manager is not None:
                manager.abort()


class DocumentUpdaterProcess(BaseIndexUpdaterProcess):
    """Document updater process"""

    def update_index(self, client, document_id, **kwargs):
        """Update document attributes in Elasticsearch index

        Document ID must be provided as an Elasticsearch ID, as document as
        already been removed from ZODB.
        """
        intids = get_utility(IIntIds)
        document = intids.queryObject(document_id)
        if document is None:
            LOGGER.warning(f"Can't find requested document {document_id}!")
            return
        # update document
        attrs = kwargs.pop('attrs', ())
        LOGGER.debug(f"Starting updating for {document!r}")
        manager = ITransactionManager(document, None)
        try:
            for attempt in manager.attempts():
                with attempt as t:
                    client.update_object(document, attrs, **kwargs)
                if t.status == COMMITTED_STATUS:
                    break
        finally:
            if manager is not None:
                manager.abort()


class DocumentUnindexProcess(BaseIndexUpdaterProcess):
    """Document un-index process"""

    def update_index(self, client, document_id, **kwargs):
        """Remove document from Elasticsearch index

        Document ID must be provided as an Elasticsearch ID, as document as
        already been removed from ZODB.
        """
        LOGGER.debug(f"Starting removal for document {document_id}")
        intids = get_utility(IIntIds)
        manager = ITransactionManager(intids, None)
        try:
            for attempt in manager.attempts():
                with attempt as t:
                    client.delete_document(document_id, safe=True)
                if t.status == COMMITTED_STATUS:
                    break
        finally:
            if manager is not None:
                manager.abort()


class ContentIndexerThread(Thread):
    """Content indexer thread"""

    def __init__(self, process):
        super().__init__()
        self.process = process

    def run(self):
        self.process.start()
        self.process.join()


class ContentIndexerHandler:
    """Elasticsearch indexer handler"""

    process = None

    @staticmethod
    def ping(settings):
        """Content indexer ping handler"""
        return [200, 'pong']

    @staticmethod
    def test(settings):  # pylint: disable=unused-argument
        """Content indexer test handler"""
        messages = [
            'OK - Documents indexer process ready to handle requests.', ''
        ]
        registry = get_pyramid_registry()
        es_client = client_from_config(registry.settings)
        if es_client is None:
            messages.append('WARNING: no Elasticsearch client available!')
        else:
            messages.extend([
                "Elasticsearch client properties:",
                " - nodes:"
            ])
            for config in es_client.es.transport.node_pool.node_selector.node_configs:
                messages.extend([
                    f"{' ' * 6}{line}"
                    for line in pformat(config, indent=5).split('\n')
                ])
            messages.extend([
                f" - index name: {es_client.index}",
                f" - indexing: {'DISABLED' if es_client.disable_indexing else 'enabled'}",
                ""
            ])
            ping = es_client.es.ping()
            messages.append(f"Server ping: {'OK' if ping else 'KO'}")
            if ping:
                messages.extend(['', 'Server info:'])
                messages.extend(pformat(es_client.es.info().body).split('\n'))
        return [200, '\n'.join(messages)]

    @staticmethod
    def index_document(settings):
        """Add or update document in Elasticsearch index"""
        registry = get_pyramid_registry()
        ContentIndexerThread(DocumentIndexProcess(registry, settings)).start()
        return [200, 'Content indexer process started']

    @staticmethod
    def update_document(settings):
        """Update document attributes in Elasticsearch index"""
        registry = get_pyramid_registry()
        ContentIndexerThread(DocumentUpdaterProcess(registry, settings)).start()

    @staticmethod
    def unindex_document(settings):
        """Remove document from Elasticsearch index"""
        registry = get_pyramid_registry()
        ContentIndexerThread(DocumentUnindexProcess(registry, settings)).start()
        return [200, 'Content un-index process started']


class ContentIndexerMessageHandler(ZMQMessageHandler):
    """Elasticsearch indexer message handler"""

    handler = ContentIndexerHandler


@implementer(IContentIndexerProcess)
class ContentIndexerProcess(ZMQProcess):
    """Elasticsearch indexer process"""
