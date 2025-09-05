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

"""PyAMS_content_es.component.gallery module

This module index content extensions for media galleries.
"""

from pyams_content.component.gallery import IBaseGallery, IGallery, IGalleryTarget
from pyams_content_es.component import get_index_values
from pyams_content_es.interfaces import IDocumentIndexInfo
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@adapter_config(context=IBaseGallery,
                provides=IDocumentIndexInfo)
def gallery_index_info(gallery):
    """Gallery index info"""
    info = {}
    get_index_values(gallery, info,
                     i18n_fields=('title', 'description'))
    for image in gallery.get_visible_images():
        get_index_values(image, info,
                         fields=('author',),
                         i18n_fields=('title', 'description', 'author_comments',
                                      'sound_title', 'sound_description'))
    return info


@adapter_config(name='gallery',
                required=IGalleryTarget,
                provides=IDocumentIndexInfo)
def gallery_target_index_info(context):
    """Gallery target index info"""
    gallery = IGallery(context)
    info = IDocumentIndexInfo(gallery, None)
    return {
        'body': info
    }
