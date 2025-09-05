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

"""PyAMS_*** module

"""

__docformat__ = 'restructuredtext'

from elasticsearch_dsl import Q
from zope.intid.interfaces import IIntIds

from pyams_content.component.thesaurus.interfaces import ICollectionsManager, ITagsManager, IThemesManager
from pyams_content.shared.view.interfaces import IWfView
from pyams_content.shared.view.interfaces.settings import IViewCollectionsSettings, IViewTagsSettings, \
    IViewThemesSettings
from pyams_content_es.shared.view.interfaces import IEsViewQueryParamsExtension, IEsViewUserQuery
from pyams_thesaurus.interfaces.thesaurus import IThesaurus
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.registry import get_utility


#
# Tags queries
#

@adapter_config(name='tags',
                required=IWfView,
                provides=IEsViewQueryParamsExtension)
class EsViewTagsQueryParamsExtension(ContextAdapter):
    """Elasticsearch view tags query params extension"""

    weight = 50

    def get_params(self, context, request=None):
        """Query params getter"""
        settings = IViewTagsSettings(self.context)
        tags = settings.get_tags_index(context)
        if tags:
            yield Q('terms',
                    **{'tags': tags})
        elif settings.select_context_tags:
            yield None


@adapter_config(name='tags',
                required=IWfView,
                provides=IEsViewUserQuery)
class EsViewTagsUserQuery(ContextAdapter):
    """Elasticsearch view tags user params"""

    weight = 50

    @staticmethod
    def get_user_params(request):
        """Query user params getter"""
        tags = request.params.getall('tag')
        if not tags:
            return
        manager = ITagsManager(request.root, None)
        if manager is None:
            return
        thesaurus = get_utility(IThesaurus, name=manager.thesaurus_name)
        if thesaurus is None:
            return
        if isinstance(tags, str):
            tags = tags.split(',')
        intids = get_utility(IIntIds)
        yield Q('terms',
                **{'tags': [
                    intids.queryId(term)
                    for term in [
                        thesaurus.terms.get(value)
                        for tag in tags
                        for value in tag.split(',')
                    ]
                    if term is not None
                ]})


#
# Themes queries
#

@adapter_config(name='themes',
                required=IWfView,
                provides=IEsViewQueryParamsExtension)
class EsViewThemesQueryParamsExtension(ContextAdapter):
    """Elasticsearch view themes query params extension"""

    weight = 52

    def get_params(self, context, request=None):
        """Query params getter"""
        settings = IViewThemesSettings(self.context)
        tags = settings.get_themes_index(context)
        if tags:
            yield Q('terms',
                    **{'themes.terms': tags})
        elif settings.select_context_themes:
            yield None


@adapter_config(name='themes',
                required=IWfView,
                provides=IEsViewUserQuery)
class EsViewThemesUserQuery(ContextAdapter):
    """Elasticsearch view themes user params"""

    weight = 52

    @staticmethod
    def get_user_params(request):
        """Query user params getter"""
        themes = request.params.getall('theme')
        if not themes:
            return
        manager = IThemesManager(request.root, None)
        if manager is None:
            return
        thesaurus = get_utility(IThesaurus, name=manager.thesaurus_name)
        if thesaurus is None:
            return
        if isinstance(themes, str):
            themes = themes.split(',')
        intids = get_utility(IIntIds)
        yield Q('terms',
                **{'themes.terms': [
                    intids.queryId(term)
                    for term in [
                        thesaurus.terms.get(value)
                        for theme in themes
                        for value in theme.split(',')
                    ]
                    if term is not None
                ]})


#
# Collections queries
#

@adapter_config(name='collections',
                required=IWfView,
                provides=IEsViewQueryParamsExtension)
class EsViewCollectionsQueryParamsExtension(ContextAdapter):
    """Elasticsearch view collections query params extension"""

    weight = 54

    def get_params(self, context, request=None):
        """Query params getter"""
        settings = IViewCollectionsSettings(self.context)
        tags = settings.get_collections_index(context)
        if tags:
            yield Q('terms',
                    **{'collections': tags})
        elif settings.select_context_collections:
            yield None


@adapter_config(name='collections',
                required=IWfView,
                provides=IEsViewUserQuery)
class EsViewCollectionsUserQuery(ContextAdapter):
    """Elasticsearch view collections user params"""

    weight = 54

    @staticmethod
    def get_user_params(request):
        """Query user params getter"""
        collections = request.params.getall('collection')
        if not collections:
            return
        manager = ICollectionsManager(request.root, None)
        if manager is None:
            return
        thesaurus = get_utility(IThesaurus, name=manager.thesaurus_name)
        if thesaurus is None:
            return
        if isinstance(collections, str):
            collections = collections.split(',')
        intids = get_utility(IIntIds)
        yield Q('terms',
                **{'collections': [
                    intids.queryId(term)
                    for term in [
                        thesaurus.terms.get(value)
                        for collection in collections
                        for value in collection.split(',')
                    ]
                    if term is not None
                ]})
