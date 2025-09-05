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

import transaction
from elasticsearch.exceptions import NotFoundError, TransportError

from pyams_content_es.interfaces import IContentIndexerUtility, IDocumentIndexTarget, \
    LOGGER
from pyams_elastic.include import client_from_config
from pyams_layer.skin import apply_skin
from pyams_site.site import site_factory
from pyams_utils.finder import find_objects_providing
from pyams_utils.registry import query_utility, set_local_registry
from pyams_zmi.skin import AdminSkin
from pyams_zmi.utils import get_object_hint, get_object_label


class Args:
    """Args converter class"""

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def __getattr__(self, item):
        """Argument value getter"""
        return self.get(item)

    def get(self, item, default=None):
        """Argument value getter with default"""
        return self.kwargs.get(item, getattr(self.args, item, default))


def index_site(request, autocommit=True, cmd_args=None, **kwargs):
    """Update Elasticsearch index with all database contents"""
    args = Args(cmd_args, kwargs)
    application = site_factory(request)
    if application is not None:
        try:
            set_local_registry(application.getSiteManager())
            indexer = query_utility(IContentIndexerUtility)
            if indexer is None:
                print("Can't find content indexer utility! Aborting...")
            else:

                from pyams_content.shared.common.interfaces import IWfSharedContent

                if args.root is not None:
                    for path in filter(bool, args.root.split('/')):
                        application = application[path]

                apply_skin(request, AdminSkin)
                client = client_from_config(request.registry.settings,
                                            timeout=args.timeout,
                                            use_transaction=False)
                for document in find_objects_providing(application, IDocumentIndexTarget):
                    try:
                        if args.verbose:
                            print(f"Indexing {get_object_hint(document, request)}: "
                                  f"{get_object_label(document, request)} ({document.id})",
                                  end='')
                        if (args.include or args.exclude) and \
                                IWfSharedContent.providedBy(document):
                            if (args.include and document.content_type not in args.include) or \
                                    (args.exclude and document.content_type in args.exclude):
                                if args.verbose:
                                    print(": ignored")
                                else:
                                    print(".", end=' ')
                                continue
                        if args.check:
                            try:
                                client.get(document)
                            except NotFoundError:
                                pass
                            else:
                                if args.verbose:
                                    print(": found")
                                else:
                                    print('-', end=' ')
                                continue
                        try:
                            client.index_object(document)
                        except TransportError:
                            if args.verbose:
                                print("   > TransportError: can't index document")
                            else:
                                print(f"(!! {document.id} !!)", end=' ')
                        else:
                            if args.verbose:
                                print(": index OK")
                            else:
                                print(f"(+{document.id})", end=' ')
                        if autocommit:
                            transaction.commit()
                    except:
                        LOGGER.exception("Error indexing document:")
        finally:
            set_local_registry(None)
        if autocommit:
            transaction.commit()
    return application
