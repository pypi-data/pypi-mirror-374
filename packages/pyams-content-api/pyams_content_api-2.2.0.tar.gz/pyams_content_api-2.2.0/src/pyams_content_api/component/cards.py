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

from pyams_content.component.cards import ICardsParagraph
from pyams_content_api.component.paragraph import JSONBaseParagraphExporter
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_i18n.interfaces import II18n
from pyams_portal.portlets.cards import ICard, ICardsContainer
from pyams_utils.adapter import adapter_config
from pyams_utils.url import absolute_url


@adapter_config(required=(ICardsParagraph, IRequest),
                provides=IJSONExporter)
class JSONCardsParagraphExporter(JSONBaseParagraphExporter):
    """JSON cards paragraph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        cards = []
        registry = self.request.registry
        container = ICardsContainer(self.context)
        for card in container.get_visible_items():
            exporter = registry.queryMultiAdapter((card, self.request), IJSONExporter)
            if exporter is not None:
                output = exporter.to_json(**params)
                if output:
                    cards.append(output)
        if cards:
            result['cards'] = cards
        return result


@adapter_config(required=(ICard, IRequest),
                provides=IJSONExporter)
class JSONCardExporter(JSONBaseExporter):
    """JSON card exporter"""
    
    def convert_content(self, **params):
        result = {}
        lang = params.get('lang')
        self.get_i18n_attribute(result, 'title', lang=lang)
        self.get_i18n_attribute(result, 'body', lang=lang)
        self.get_image_attribute(result, 'illustration')
        i18n = II18n(self.context)
        button = {
            'status': self.context.button_status,
            'css_class': self.context.css_class
        }
        button_label = i18n.query_attribute('button_label', lang=lang)
        target = self.context.get_target(request=self.request)
        if target is not None:
            button.update({
                'title': button_label or II18n(target).query_attribute('title', lang=lang),
                'href': absolute_url(target, self.request)
            })
            result['button'] = button
        elif self.context.target_url:
            button.update({
                'title': button_label,
                'href': self.context.target_url
            })
            result['button'] = button
        return result
    