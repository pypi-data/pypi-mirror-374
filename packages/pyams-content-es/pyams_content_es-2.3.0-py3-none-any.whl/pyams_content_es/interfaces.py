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

"""PyAMS_content_es.interfaces module

"""

import logging
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import Interface
from zope.schema import Choice, TextLine

from pyams_utils.interfaces import ZODB_CONNECTIONS_VOCABULARY_NAME
from pyams_utils.schema import TextLineListField
from pyams_zmq.interfaces import IZMQProcess

from pyams_content_es import _


#
# Content indexer utility
#

LOGGER = logging.getLogger('PyAMS (ES content)')


INDEXER_NAME = 'Elasticsearch indexer'
INDEXER_LABEL = _("Elasticsearch documents indexer")


INDEXER_PREFIX = 'pyams_content_es'
INDEXER_STARTER_KEY = f'{INDEXER_PREFIX}.start_handler'
INDEXER_HANDLER_KEY = f'{INDEXER_PREFIX}.tcp_handler'
INDEXER_AUTH_KEY = f'{INDEXER_PREFIX}.allow_auth'
INDEXER_CLIENTS_KEY = f'{INDEXER_PREFIX}.allow_clients'


class IContentIndexerProcess(IZMQProcess):
    """Content indexer process"""


class IContentIndexerHandler(Interface):
    """Content indexer handler interface"""


class IContentIndexerUtility(IAttributeAnnotatable):
    """Content indexer utility interface"""

    zodb_name = Choice(title=_("ZODB connection name"),
                       description=_("Name of ZODB defining document indexer connection"),
                       required=False,
                       default='',
                       vocabulary=ZODB_CONNECTIONS_VOCABULARY_NAME)

    def get_socket(self):
        """ØMQ socket getter"""

    def test_process(self):
        """Test document indexer process connection"""

    def index_document(self, document):
        """Add or update document to Elasticsearch index"""

    def unindex_document(self, document):
        """Remove document from Elasticsearch index"""


class IDocumentIndexInfo(Interface):
    """Document index info"""


class IDocumentIndexTarget(Interface):
    """Document index target marker interface"""


#
# Search settings interfaces
#

class IBaseSearchSettings(Interface):
    """Base search settings interface"""

    analyzer = TextLine(title=_("Search analyzer"),
                        description=_("Used search analyzer; check index settings to get list of "
                                      "available analyzers..."),
                        required=True,
                        default='default')

    default_operator = Choice(title=_("Default operator"),
                              description=_("This is the default operator used to combine search terms"),
                              values=('AND', 'OR'),
                              required=True,
                              default='AND')


QUICK_SEARCH_SETTINGS_KEY = 'pyams_content_es.quick_settings'


class IQuickSearchSettings(IBaseSearchSettings):
    """Backoffice quick search settings interface"""

    search_fields = TextLineListField(title=_("Search fields"),
                                      description=_("List of fields used for quick search in backoffice, "
                                                    "with their respective weight (if any)"),
                                      required=True,
                                      default=[
                                          'title.*',
                                          'short_name.*',
                                          'header.*',
                                          'description.*'
                                      ])


USER_SEARCH_SETTINGS_KEY = 'pyams_content_es.user_settings'


class IUserSearchSettings(IBaseSearchSettings):
    """Default user search settings"""

    search_fields = TextLineListField(title=_("Backoffice search fields"),
                                      description=_("List of fields used for base search in backoffice, "
                                                    "with their respective weight (if any)"),
                                      required=True,
                                      default=[
                                          'title.*',
                                          'short_name.*',
                                          'header.*',
                                          'description.*'
                                      ])

    fulltext_search_fields = TextLineListField(title=_("Fulltext search fields"),
                                               description=_("List of fields used for fulltext search, "
                                                             "with their respective weight (if any)"),
                                               required=True,
                                               default=[
                                                   'title.*',
                                                   'short_name.*',
                                                   'header.*',
                                                   'description.*'
                                               ])
