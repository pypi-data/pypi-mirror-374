# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

__docformat__ = 'restructuredtext'

from pyramid.interfaces import IRequest

from pyams_content.component.gallery import IGalleryFile
from pyams_content.component.gallery.interfaces import IGalleryParagraph
from pyams_content_api.component.paragraph import JSONBaseParagraphExporter
from pyams_content_api.feature.json import JSONBaseExporter
from pyams_content_api.feature.json.interfaces import IJSONExporter
from pyams_utils.adapter import adapter_config


@adapter_config(required=(IGalleryParagraph, IRequest),
                provides=IJSONExporter)
class JSONGalleryParagraphExporter(JSONBaseParagraphExporter):
    """JSON gallery paragraph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        medias = []
        registry = self.request.registry
        for media in self.context.get_visible_medias():
            exporter = registry.queryMultiAdapter((media, self.request), IJSONExporter)
            if exporter is not None:
                output = exporter.to_json(**params)
                if output:
                    medias.append(output)
        if medias:
            result['medias'] = medias
        return result
    
    
@adapter_config(required=(IGalleryFile, IRequest),
                provides=IJSONExporter)
class JSONGalleryFileExporter(JSONBaseExporter):
    """JSON gallery file exporter"""
    
    def convert_content(self, **params):
        result = {}
        lang = params.get('lang')
        self.get_i18n_attribute(result, 'title', lang=lang)
        self.get_i18n_attribute(result, 'alt_title', lang=lang)
        self.get_i18n_attribute(result, 'description', lang=lang)
        self.get_attribute(result, 'author')
        self.get_image_attribute(result, 'data', name='media', **params)
        audio = {}
        self.get_file_attribute(audio, 'sound', name='audio', **params)
        if audio:
            self.get_i18n_attribute(audio, 'sound_title', lang=lang, name='title')
            self.get_i18n_attribute(audio, 'sound_description', lang=lang, name='description')
            result['audio'] = audio
        return result
    