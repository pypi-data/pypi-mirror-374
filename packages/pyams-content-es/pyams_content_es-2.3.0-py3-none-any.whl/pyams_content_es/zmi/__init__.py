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

"""PyAMS_content_es.zmi module

This module defines a few components used to handle Elasticsearch content
indexer utility properties.
"""

from zope.interface import Interface

from pyams_content_es.interfaces import IContentIndexerUtility, INDEXER_LABEL, IQuickSearchSettings, IUserSearchSettings
from pyams_form.ajax import ajax_form_config
from pyams_form.button import Buttons, handler
from pyams_form.field import Fields
from pyams_form.interfaces.form import IFormContent, IGroup, IInnerSubForm
from pyams_form.subform import InnerDisplayForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces.base import MANAGE_SYSTEM_PERMISSION
from pyams_skin.interfaces.view import IModalPage
from pyams_skin.schema.button import ActionButton
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config
from pyams_utils.url import absolute_url
from pyams_zmi.form import AdminModalDisplayForm, AdminModalEditForm, FormGroupSwitcher
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel
from pyams_zmi.interfaces.form import IFormTitle, IModalEditFormButtons
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.table import TableElementEditor
from pyams_zmi.utils import get_object_label

__docformat__ = 'restructuredtext'

from pyams_content_es import _


@adapter_config(required=(IContentIndexerUtility, IPyAMSLayer, Interface),
                provides=IObjectLabel)
def content_indexer_label(context, request, view):
    """Content indexer label"""
    return request.localizer.translate(INDEXER_LABEL)


@adapter_config(required=(IContentIndexerUtility, IAdminLayer, Interface),
                provides=ITableElementEditor)
class ContentIndexerElementEditor(TableElementEditor):
    """Content index element editor"""

    def __new__(cls, context, request, view):
        if not request.has_permission(MANAGE_SYSTEM_PERMISSION, context=context):
            return None
        return TableElementEditor.__new__(cls)


class IContentIndexerPropertiesEditFormButtons(IModalEditFormButtons):
    """Content indexer properties edit form buttons"""

    test = ActionButton(name='test',
                        title=_("Test connection"))


@ajax_form_config(name='properties.html',
                  context=IContentIndexerUtility, layer=IPyAMSLayer,
                  permission=MANAGE_SYSTEM_PERMISSION)
class ContentIndexerPropertiesEditForm(AdminModalEditForm):
    """Content indexer properties edit form"""

    modal_class = 'modal-xl'
    legend = _("Document indexer properties")
    fields = Fields(IContentIndexerUtility)
    buttons = Buttons(IContentIndexerPropertiesEditFormButtons).select('test', 'apply', 'close')

    def update_actions(self):
        super().update_actions()
        test = self.actions.get('test')
        if test is not None:
            test.add_class('btn-info mr-auto')
            test.href = absolute_url(self.context, self.request, 'test-indexer.html')
            test.modal_target = True

    @handler(IContentIndexerPropertiesEditFormButtons['apply'])
    def handle_apply(self, action):
        """Apply button handler"""
        super().handle_apply(self, action)


@adapter_config(required=(IContentIndexerUtility, IAdminLayer, IModalPage),
                provides=IFormTitle)
def content_indexer_form_title(context, request, view):
    return get_object_label(context, request, view)


class ContentIndexerSettingsGroup(FormGroupSwitcher):
    """Content indexer settings group"""

    switcher_mode = 'always'

    def update_widgets(self, prefix=None, use_form_mode=True):
        super().update_widgets(prefix, use_form_mode)
        fields = self.widgets.get('search_fields')
        if fields is not None:
            fields.rows = 8


@adapter_config(name='quick-settings',
                required=(IContentIndexerUtility, IAdminLayer, ContentIndexerPropertiesEditForm),
                provides=IGroup)
class ContentIndexerQuickSearchSettingsGroup(ContentIndexerSettingsGroup):
    """Content index quick search settings group"""

    legend = _("Quick search settings")

    prefix = 'quick_settings.'
    fields = Fields(IQuickSearchSettings)
    weight = 10


@adapter_config(required=(IContentIndexerUtility, IAdminLayer, ContentIndexerQuickSearchSettingsGroup),
                provides=IFormContent)
def content_indexer_quick_search_settings_content(context, request, group):
    """Content indexer quick search settings edit form group content getter"""
    return IQuickSearchSettings(context)


@adapter_config(name='user-settings',
                required=(IContentIndexerUtility, IAdminLayer, ContentIndexerPropertiesEditForm),
                provides=IGroup)
class ContentIndexerUserSearchSettingsGroup(ContentIndexerSettingsGroup):
    """Content index user search settings group"""

    legend = _("User search settings")

    prefix = 'user_settings.'
    fields = Fields(IUserSearchSettings).select('analyzer', 'search_fields',
                                                'fulltext_search_fields', 'default_operator')
    weight = 20

    def update_widgets(self, prefix=None, use_form_mode=True):
        super().update_widgets(prefix, use_form_mode)
        fields = self.widgets.get('fulltext_search_fields')
        if fields is not None:
            fields.rows = 8


@adapter_config(required=(IContentIndexerUtility, IAdminLayer, ContentIndexerUserSearchSettingsGroup),
                provides=IFormContent)
def content_indexer_user_search_group_content(context, request, group):
    """Content indexer user search settings edit form group content getter"""
    return IUserSearchSettings(context)


#
# Indexer test form
#

@ajax_form_config(name='test-indexer.html',
                  context=IContentIndexerUtility, layer=IPyAMSLayer,
                  permission=MANAGE_SYSTEM_PERMISSION)
class ContentIndexerTestForm(AdminModalDisplayForm):
    """Content indexer test form"""


@adapter_config(name='test',
                required=(IContentIndexerUtility, IAdminLayer, ContentIndexerTestForm),
                provides=IInnerSubForm)
@template_config(template='templates/test-indexer.pt', layer=IAdminLayer)
class ContentIndexerTestStatusForm(InnerDisplayForm):
    """Content indexer test status form"""

    legend = _("Content indexer test")

    def test(self):
        """Content indexer test"""
        return self.context.test_process()
