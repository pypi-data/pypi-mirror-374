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
from pyams_content.component.paragraph.interfaces.html import IHTMLParagraph, IRawParagraph
from pyams_content.feature.renderer import IContentRenderer
from pyams_content_api.component.paragraph import JSONBaseParagraphExporter
from pyams_content_api.feature.json import IJSONExporter
from pyams_utils.adapter import adapter_config


@adapter_config(required=(IRawParagraph, IRequest),
                provides=IJSONExporter)
class JSONRawParagraphExporter(JSONBaseParagraphExporter):
    """JSON raw paragraph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        renderer = self.request.registry.queryMultiAdapter((self.context, self.request),
                                                           IContentRenderer,
                                                           name=self.context.renderer)
        if renderer is not None:
            result['body'] = renderer.body
        return result


@adapter_config(required=(IHTMLParagraph, IRequest),
                provides=IJSONExporter)
class JSONHTMLParagraphExporter(JSONBaseParagraphExporter):
    """JSON HTML paragraph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        self.get_html_attribute(result, 'body', lang=params.get('lang'))
        return result
  