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

from pyams_content.component.video.interfaces import IExternalVideoParagraph
from pyams_content_api.component.paragraph import JSONBaseParagraphExporter
from pyams_content_api.feature.json import IJSONExporter
from pyams_utils.adapter import adapter_config


@adapter_config(required=(IExternalVideoParagraph, IRequest),
                provides=IJSONExporter)
class JSONExternalVideoParagraphExporter(JSONBaseParagraphExporter):
    """JSON external video paragaph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        lang = params.get('lang')
        self.get_attribute(result, 'author')
        self.get_i18n_attribute(result, 'description', lang=lang)
        self.get_attribute(result, 'provider_name')
        self.get_attribute(result, 'video_id', context=self.context.settings)
        return result
    