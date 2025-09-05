#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS content ES.include module

This module is used for Pyramid integration
"""
import atexit
import os
import re
import sys
from pyramid.events import subscriber
from pyramid.interfaces import IApplicationCreated
from pyramid.settings import asbool

from pyams_content_es.interfaces import INDEXER_AUTH_KEY, INDEXER_CLIENTS_KEY, \
    INDEXER_HANDLER_KEY, INDEXER_NAME, \
    INDEXER_STARTER_KEY, \
    LOGGER
from pyams_content_es.process import ContentIndexerMessageHandler, ContentIndexerProcess
from pyams_site.interfaces import PYAMS_APPLICATION_DEFAULT_NAME, PYAMS_APPLICATION_SETTINGS_KEY
from pyams_utils.protocol.tcp import is_port_in_use
from pyams_utils.registry import get_pyramid_registry, set_local_registry
from pyams_utils.zodb import get_connection_from_settings
from pyams_zmq.process import process_exit_func


__docformat__ = 'restructuredtext'


def include_package(config):
    """Pyramid package include"""

    # add translations
    config.add_translation_dirs('pyams_content_es:locales')

    # override PyAMS_content package components
    config.include('pyams_content')

    try:
        import pyams_zmi  # pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        config.scan(ignore=[re.compile(r'pyams_content_es\..*\.zmi\.?.*').search])
    else:
        config.scan()


@subscriber(IApplicationCreated)
def handle_new_application(event):
    """Start Elasticsearch document indexer when application is created"""

    # Check for PyAMS command line script
    cmdline = os.path.split(sys.argv[0])[-1]
    if cmdline.startswith('pyams_'):
        return

    registry = get_pyramid_registry()
    settings = registry.settings
    start_handler = asbool(settings.get(INDEXER_STARTER_KEY, False))
    if not start_handler:
        return

    # check if port is available
    handler_address = settings.get(INDEXER_HANDLER_KEY, '127.0.0.1:5557')
    hostname, port = handler_address.split(':')
    if is_port_in_use(int(port), hostname):
        LOGGER.warning("Elasticsearch indexer port already used, aborting...")
        return

    # get database connection
    connection = get_connection_from_settings(settings)
    root = connection.root()
    # get application
    application_name = settings.get(PYAMS_APPLICATION_SETTINGS_KEY,
                                    PYAMS_APPLICATION_DEFAULT_NAME)
    application = root.get(application_name)
    if application is None:
        return

    process = None
    sm = application.getSiteManager()
    set_local_registry(sm)
    try:
        indexer = sm.get(INDEXER_NAME)
        if indexer is None:
            return
        # create indexer process
        process = ContentIndexerProcess(handler_address,
                                        ContentIndexerMessageHandler,
                                        settings.get(INDEXER_AUTH_KEY),
                                        settings.get(INDEXER_CLIENTS_KEY),
                                        registry)
        LOGGER.info(f"Starting Elasticsearch documents indexer {process!r}...")
        process.start()
        if process.is_alive():
            atexit.register(process_exit_func, process=process)
            LOGGER.info(f"Started Elasticsearch documents indexer with PID {process.pid}.")
    finally:
        if process and not process.is_alive():
            process.terminate()
            process.join()
        set_local_registry(None)
