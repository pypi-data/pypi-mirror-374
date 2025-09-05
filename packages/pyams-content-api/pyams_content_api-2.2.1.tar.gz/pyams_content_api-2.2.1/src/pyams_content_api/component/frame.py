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

from pyams_content.component.frame import IFrameParagraph
from pyams_content_api.component.paragraph import JSONBaseParagraphExporter
from pyams_content_api.feature.json import IJSONExporter
from pyams_utils.adapter import adapter_config


@adapter_config(required=(IFrameParagraph, IRequest),
                provides=IJSONExporter)
class JSONFrameParagraphExporter(JSONBaseParagraphExporter):
    """JSON frame paragraph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        self.get_html_attribute(result, 'body', lang=params.get('lang'))
        return result
    