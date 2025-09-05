# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from pyramid.interfaces import IRequest

from pyams_content.component.links import IBaseLink, IExternalLink, IInternalLink, IMailtoLink
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@adapter_config(required=(IBaseLink, IRequest),
                provides=IJSONExporter)
class JSONBaseLinkExporter(JSONBaseExporter):
    """JSON base link exporter"""
    
    def convert_content(self, **params):
        result = {}
        lang = params.get('lang')
        self.get_i18n_attribute(result, 'title', lang=lang)
        self.get_i18n_attribute(result, 'description', lang=lang)
        self.get_data_attribute(result, 'pictogram', **params)
        return result
    
    
@adapter_config(required=(IInternalLink, IRequest),
                provides=IJSONExporter)
class JSONInternalLinkExporter(JSONBaseLinkExporter):
    """JSON internal link exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        result['factory'] = 'internal_link'
        result['href'] = self.context.get_url(self.request)
        return result


@adapter_config(required=(IExternalLink, IRequest),
                provides=IJSONExporter)
class JSONExternalLinkExporter(JSONBaseLinkExporter):
    """JSON external link exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        result['factory'] = 'external_link'
        result['href'] = self.context.get_url(self.request)
        return result


@adapter_config(required=(IMailtoLink, IRequest),
                provides=IJSONExporter)
class JSONMailtoLinkExporter(JSONBaseLinkExporter):
    """JSON mailto link exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        result['factory'] = 'mailto_link'
        self.get_attribute(result, 'address')
        self.get_attribute(result, 'address_name')
        return result
