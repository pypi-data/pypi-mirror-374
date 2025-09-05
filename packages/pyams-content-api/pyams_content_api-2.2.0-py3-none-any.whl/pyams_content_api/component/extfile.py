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

from pyams_content.component.extfile import IBaseExtFile
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_utils.adapter import adapter_config


@adapter_config(required=(IBaseExtFile, IRequest),
                provides=IJSONExporter)
class JSONBaseExtFileExporter(JSONBaseExporter):
    """JSON base external file exporter"""
    
    def convert_content(self, **params):
        result = {}
        lang = params.get('lang')
        self.get_i18n_attribute(result, 'title', lang=lang)
        self.get_i18n_attribute(result, 'description', lang=lang)
        self.get_attribute(result, 'author')
        self.get_file_attribute(result, 'data', lang=lang)
        return result
    