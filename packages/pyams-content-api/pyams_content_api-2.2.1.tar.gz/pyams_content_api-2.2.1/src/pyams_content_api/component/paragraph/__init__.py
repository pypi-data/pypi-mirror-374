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

from pyams_content.component.paragraph import IBaseParagraph, IParagraphContainer, IParagraphContainerTarget
from pyams_content.component.paragraph.interfaces.group import IParagraphsGroup
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@adapter_config(name='paragraphs',
                required=(IParagraphContainerTarget, IRequest),
                provides=IJSONExporter)
class JSONParagraphsExporter(JSONBaseExporter):
    """JSON paragraphs exporter"""
    
    is_inner = True
    conversion_target = None
    
    def convert_content(self, **params):
        """JSON paragraphs exporter"""
        results = []
        registry = self.request.registry
        container = IParagraphContainer(self.context, None)
        for paragraph in container.get_visible_paragraphs():
            result = {}
            for name, converter in registry.getAdapters((paragraph, self.request),
                                                        IJSONExporter):
                if (('included' in params) and
                    (name not in params['included'].split(','))) or \
                        (('excluded' in params) and
                         (name in params['excluded'].split(','))):
                    continue
                output = converter.to_json(**params)
                if not output:
                    continue
                if converter.is_inner:
                    result.update({name: output})
                else:
                    result.update(output)
            if result:
                results.append(result)
        return results


@adapter_config(required=(IBaseParagraph, IRequest),
                provides=IJSONExporter)
class JSONBaseParagraphExporter(JSONBaseExporter):
    """JSON base paragraph exporter"""
    
    is_inner = False
    conversion_target = None
    
    def convert_content(self, **params):
        """JSON base paragraph exporter"""
        context = self.context
        result = {
            'factory': context.factory_name,
            'factory_label': self.request.localizer.translate(context.factory_label),
            'renderer': context.renderer,
            'locked': context.locked,
            'anchor': context.anchor
        }
        self.get_i18n_attribute(result, 'title', lang=params.get('lang'))
        return result


@adapter_config(required=(IParagraphsGroup, IRequest),
                provides=IJSONExporter)
class JSONParagraphsGroupExporter(JSONBaseParagraphExporter):
    """JSON paragraphs group exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        registry = self.request.registry
        paragraphs = []
        for paragraph in IParagraphContainer(self.context).get_visible_paragraphs():
            data = {}
            for name, converter in registry.getAdapters((paragraph, self.request),
                                                        IJSONExporter):
                if (('included' in params) and
                    (name not in params['included'].split(','))) or \
                        (('excluded' in params) and
                         (name in params['excluded'].split(','))):
                    continue
                output = converter.to_json(**params)
                if not output:
                    continue
                if converter.is_inner:
                    data.update({name: output})
                else:
                    data.update(output)
            if data:
                paragraphs.append(data)
        result['paragraphs'] = paragraphs
        return result
    