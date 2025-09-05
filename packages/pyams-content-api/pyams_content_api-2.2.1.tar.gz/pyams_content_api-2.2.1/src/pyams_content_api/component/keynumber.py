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

from pyams_content.component.keynumber import IKeyNumberInfo, IKeyNumbersContainer, IKeyNumbersParagraph
from pyams_content_api.component.paragraph import JSONBaseParagraphExporter
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@adapter_config(required=(IKeyNumbersParagraph, IRequest),
                provides=IJSONExporter)
class JSONKeyNumbersParagraphExporter(JSONBaseParagraphExporter):
    """JSON key numbers paragraph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        numbers = []
        registry = self.request.registry
        container = IKeyNumbersContainer(self.context)
        for number in container.get_visible_items():
            exporter = registry.queryMultiAdapter((number, self.request), IJSONExporter)
            if exporter is not None:
                output = exporter.to_json(**params)
                if output:
                    numbers.append(output)
        if numbers:
            result['numbers'] = numbers
        return result
    
    
@adapter_config(required=(IKeyNumberInfo, IRequest),
                provides=IJSONExporter)
class JSONKeyNumberExporter(JSONBaseExporter):
    """JSON key number exporter"""
    
    def convert_content(self, **params):
        result = {}
        lang = params.get('lang')
        self.get_i18n_attribute(result, 'label', lang=lang)
        self.get_attribute(result, 'number')
        self.get_i18n_attribute(result, 'unit', lang=lang)
        self.get_i18n_attribute(result, 'text', lang=lang)
        return result
    