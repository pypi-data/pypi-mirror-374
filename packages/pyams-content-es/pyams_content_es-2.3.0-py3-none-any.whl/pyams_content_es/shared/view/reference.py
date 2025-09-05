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

"""PyAMS_content_es.shared.view.reference module

"""

__docformat__ = 'restructuredtext'

from elasticsearch_dsl import Q
from zope.intid.interfaces import IIntIds

from pyams_content.shared.view import IWfView
from pyams_content.shared.view.interfaces.query import EXCLUDED_VIEW_ITEMS
from pyams_content.shared.view.interfaces.settings import IViewInternalReferencesSettings, ONLY_REFERENCE_MODE
from pyams_content_es.shared.view import IEsViewQueryParamsExtension, IEsViewUserQuery
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.registry import get_utility


@adapter_config(name='references',
                required=IWfView,
                provides=IEsViewQueryParamsExtension)
class EsViewReferencesQueryParamsExtension(ContextAdapter):
    """Elasticsearch view internal references query params extension"""

    weight = 10

    def get_params(self, context, request=None):
        """Elasticsearch query params getter"""
        settings = IViewInternalReferencesSettings(self.context)
        if settings.references_mode == ONLY_REFERENCE_MODE:
            yield None
        else:
            if settings.exclude_context:
                intids = get_utility(IIntIds)
                try:
                    yield Q('bool',
                            must_not=Q('term',
                                       **{'internal_id': intids.register(context)}))
                except TypeError:
                    return


@adapter_config(name='exclusions',
                required=IWfView,
                provides=IEsViewUserQuery)
class EsExclusionsViewQueryParamsExtension(ContextAdapter):
    """Elasticsearch exclusions for Elasticsearch

    This adapter is looking into request's annotations for items which should be excluded
    from search.
    """

    @staticmethod
    def get_user_params(request):
        excluded_items = request.annotations.get(EXCLUDED_VIEW_ITEMS)
        if excluded_items:
            yield Q('bool',
                    must_not=Q('terms',
                               **{'reference_id': tuple(excluded_items)}))
