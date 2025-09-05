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

"""PyAMS_content_es.zmi.content module

This module provides components which are used to check a specific content against
Elasticsearch index.
"""

__docformat__ = 'restructuredtext'

from dateutil import parser
from elasticsearch_dsl import Search
from zope.interface import Interface, implementer
from zope.schema import TextLine
from zope.schema.fieldproperty import FieldProperty

from pyams_content.feature.search import ISearchFolder
from pyams_content.interfaces import MANAGE_CONTENT_PERMISSION
from pyams_content_es import _
from pyams_content_es.interfaces import IDocumentIndexTarget
from pyams_form.ajax import ajax_form_config
from pyams_form.button import Buttons, handler
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer, IFormContent
from pyams_i18n.interfaces import II18n
from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.viewlet import IFormHeaderViewletManager
from pyams_skin.schema.button import CloseButton, SubmitButton
from pyams_skin.viewlet.help import AlertMessage
from pyams_skin.viewlet.menu import MenuItem
from pyams_utils.adapter import ContextRequestViewAdapter, NullAdapter, adapter_config
from pyams_utils.date import format_datetime
from pyams_utils.timezone import tztime
from pyams_viewlet.viewlet import viewlet_config
from pyams_workflow.interfaces import IWorkflow
from pyams_zmi.form import AdminModalEditForm
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IContextActionsDropdownMenu


@viewlet_config(name='content-index.menu',
                context=IDocumentIndexTarget, layer=IAdminLayer,
                manager=IContextActionsDropdownMenu, weight=30,
                permission=MANAGE_CONTENT_PERMISSION)
class ContentIndexCheckerMenu(MenuItem):
    """Content index checker menu"""

    label = _("Check index content")
    icon_class = 'fas fa-check'

    href = 'content-index.html'
    modal_target = True


@viewlet_config(name='content-index.menu',
                context=ISearchFolder, layer=IAdminLayer,
                manager=IContextActionsDropdownMenu, weight=30,
                permission=MANAGE_CONTENT_PERMISSION)
class SearchFolderIndexCheckerMenu(NullAdapter):
    """Search folder index checker menu"""


class IContentIndexCheckerFormFields(Interface):
    """Content index checker form fields interface"""

    id = TextLine(title=_("Internal ID"),
                  readonly=True)

    timestamp = TextLine(title=_("Modification date"),
                         readonly=True)

    status = TextLine(title=_("Workflow status"),
                      readonly=True)


@implementer(IContentIndexCheckerFormFields)
class ContentIndexCheckerFormContent:
    """Content index checker form content"""

    id = FieldProperty(IContentIndexCheckerFormFields['id'])
    timestamp = FieldProperty(IContentIndexCheckerFormFields['timestamp'])
    status = FieldProperty(IContentIndexCheckerFormFields['status'])


class IContentIndexCheckerFormButtons(Interface):
    """Content index checker form buttons interface"""

    reindex = SubmitButton(name='reindex',
                           title=_("Force reindex"))

    close = CloseButton(name='close',
                        title=_("Cancel"))


@ajax_form_config(name='content-index.html',
                  context=IDocumentIndexTarget, layer=IPyAMSLayer,
                  permission=MANAGE_CONTENT_PERMISSION)
class ContentIndexCheckerForm(AdminModalEditForm):
    """Content index checker form"""

    subtitle = _("Index content check")
    legend = _("Current index content")

    fields = Fields(IContentIndexCheckerFormFields)
    buttons = Buttons(IContentIndexCheckerFormButtons)

    _edit_permission = MANAGE_CONTENT_PERMISSION

    @handler(buttons['reindex'])
    def handle_reindex(self, action):
        """Reindex button handle"""
        self.handle_apply(self, action)

    def apply_changes(self, data):
        client = self.request.elastic_client
        client.index_object(self.context)


@viewlet_config(name='help',
                context=IDocumentIndexTarget, layer=IAdminLayer,
                view=ContentIndexCheckerForm,
                manager=IFormHeaderViewletManager, weight=10)
class ContentIndexCheckerFormHelp(AlertMessage):
    """Content index checker form help"""

    status = 'info'

    _message = _("Documents informations are stored in an Elasticsearch index. If an error "
                 "occurs, some documents can be stored in this index with different values from "
                 "those stored into contents database.<br />"
                 "If required, this operation will try to reindex document properties into "
                 "Elasticsearch.")
    message_renderer = 'markdown'


@adapter_config(required=(IDocumentIndexTarget, IAdminLayer, ContentIndexCheckerForm),
                provides=IFormContent)
def document_index_checker_form_content(context, request, form):
    """Document index checker form content getter"""
    client = request.elastic_client
    query = Search(using=client.es, index=client.index) \
        .query('term', _id=context.id) \
        .source(['_id', '@timestamp', 'workflow'])
    content = ContentIndexCheckerFormContent()
    translate = request.localizer.translate
    for result in query.execute().hits:
        content.id = result.meta.id
        content.timestamp = format_datetime(tztime(parser.parse(result['@timestamp'])))
        content.status = translate(IWorkflow(context).get_state_label(result.workflow.status))
    return content


@adapter_config(required=(IDocumentIndexTarget, IAdminLayer, ContentIndexCheckerForm),
                provides=IAJAXFormRenderer)
class ContentIndexCheckerFormRenderer(ContextRequestViewAdapter):
    """Content index checker form renderer"""

    def render(self, changes):
        translate = self.request.localizer.translate
        return {
            'status': 'success',
            'message': translate(_("Request successful, index content has been updated"))
        }
