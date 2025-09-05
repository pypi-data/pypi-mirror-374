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

"""PyAMS_content_es.component.extfile module

This module defines adapters which are used to handle external file indexation.
"""

import base64

from pyams_content.component.extfile.interfaces import IBaseExtFile
from pyams_content.component.paragraph import IBaseParagraph
from pyams_content.component.paragraph.interfaces import IParagraphContainerTarget
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config
from pyams_utils.finder import find_objects_providing
from pyams_utils.traversing import get_parent
from pyams_workflow.interfaces import IWorkflow, IWorkflowState

__docformat__ = 'restructuredtext'


@adapter_config(name='extfile',
                required=IParagraphContainerTarget,
                provides=IDocumentIndexInfo)
def paragraph_container_extfile_index_info(context):
    """Paragraph container external file indexation info"""
    extfiles = []
    attachments = []
    workflow_state = None
    workflow = IWorkflow(context, None)
    if workflow is not None:
        workflow_state = IWorkflowState(context, None)
    # don't index attachments for contents which are not published
    if (not workflow_state) or (workflow_state.state in workflow.visible_states):
        # extract paragraphs attachments
        for extfile in find_objects_providing(context, IBaseExtFile):
            paragraph = get_parent(extfile, IBaseParagraph)
            if not paragraph.visible:
                continue
            extfiles.append({
                'title': extfile.title,
                'description': extfile.description
            })
            for lang, data in extfile.data.items():
                content_type = data.content_type
                if isinstance(content_type, bytes):
                    content_type = content_type.decode()
                if content_type.startswith('image/') or \
                        content_type.startswith('audio/') or \
                        content_type.startswith('video/'):
                    continue
                attachments.append({
                    'content_type': content_type,
                    'name': data.filename,
                    'language': lang,
                    'content': base64.encodebytes(data.data).decode().replace('\n', '')
                })
    result = {
        'extfile': extfiles
    }
    if attachments:
        result.update({
            '__pipeline__': 'attachment',
            'attachments': attachments
        })
    return result
