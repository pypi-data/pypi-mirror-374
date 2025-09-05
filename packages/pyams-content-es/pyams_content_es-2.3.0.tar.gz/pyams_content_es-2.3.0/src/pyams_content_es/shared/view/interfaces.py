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

"""PyAMS_content_es.shared.view.interfaces module

This module defines interfaces related to views management.
"""

from pyams_content.shared.view import IViewQuery
from pyams_content.shared.view.interfaces.query import IViewQueryFilterExtension, IViewQueryParamsExtension, \
    IViewUserQuery

__docformat__ = 'restructuredtext'


class IEsViewQuery(IViewQuery):
    """Elasticsearch view query marker interface

    This is the base interface of view query.
    """

    def get_post_filters(self, context, request=None, **kwargs):
        """Get static view query post-filters params

        These filters are defined as query parameters, but are applied only after
        aggregates calculation.
        """


class IEsViewQueryParamsExtension(IViewQueryParamsExtension):
    """Elasticsearch view query params extension

    This interface is used to register custom adapters which are defined to get
    Elasticsearch query extra parameters.
    """


class IEsViewUserQuery(IViewUserQuery):
    """Elasticsearch view user query interface"""


class IEsViewQueryPostFilterExtension(IViewQueryParamsExtension):
    """Elasticsearch view query post-filter extension

    This interface is used to register custom adapters which are defined to get
    Elasticsearch post-filter extra parameters; these filters are used to
    filter results after aggregates calculation.
    """


class IEsViewUserPostFilter(IViewUserQuery):
    """Elasticsearch view user post-filter interface"""


class IEsViewQueryResultsFilterExtension(IViewQueryFilterExtension):
    """Elasticsearch view query filter extension

    This interface is used to register adapters which are defined to
    filter results of Elasticsearch query. So unlike params extensions,
    """
