#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_*** module

"""

from pyramid.interfaces import IRequest

from pyams_content.component.illustration.interfaces import IBaseIllustration, IIllustration, IIllustrationParagraph, \
    IIllustrationTarget, ILinkIllustration, ILinkIllustrationTarget
from pyams_content_api.component.paragraph import JSONBaseParagraphExporter
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@adapter_config(name='link_illustration',
                required=(ILinkIllustrationTarget, IRequest),
                provides=IJSONExporter)
class JSONLinkIllustrationExporter(JSONBaseExporter):
    """JSON link illustration exporter"""
    
    is_inner = True
    conversion_target = None
    
    target_intf = ILinkIllustration

    def convert_content(self, **params):
        """JSON illustration conversion"""
        result = super().convert_content(**params)
        illustration = self.target_intf(self.context, None)
        if illustration and illustration.has_data():
            self.get_i18n_attribute(result, 'title', lang=params.get('lang'), context=illustration)
            self.get_i18n_attribute(result, 'alt_title', lang=params.get('lang'), context=illustration)
            self.get_attribute(result, 'author', context=illustration)
            self.get_image_attribute(result, 'data', name='image', context=illustration, **params)
        return result
    

@adapter_config(name='illustration',
                required=(IIllustrationTarget, IRequest),
                provides=IJSONExporter)
class JSONIllustrationExporter(JSONLinkIllustrationExporter):
    """JSON illustration exporter"""
    
    target_intf = IIllustration
    
    def convert_content(self, **params):
        """JSON link illustration conversion"""
        result = super().convert_content(**params)
        if result:
            illustration = self.target_intf(self.context)
            self.get_i18n_attribute(result, 'description', lang=params.get('lang'), context=illustration)
        return result
    

@adapter_config(required=(IIllustrationParagraph, IRequest),
                provides=IJSONExporter)
class JSONIllustrationParagraphExporter(JSONBaseParagraphExporter):
    """JSON illustration paragraph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        if result:
            exporter = JSONIllustrationExporter(self.context, self.request)
            exporter.target_intf = IBaseIllustration
            result.update(exporter.to_json(**params))
        return result
    