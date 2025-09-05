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

from pyams_content.component.contact import IContactParagraph
from pyams_content_api.component.paragraph import JSONBaseParagraphExporter
from pyams_content_api.feature.json import IJSONExporter
from pyams_i18n.interfaces import II18n
from pyams_sequence.reference import get_reference_target
from pyams_utils.adapter import adapter_config
from pyams_utils.url import absolute_url, canonical_url


@adapter_config(required=(IContactParagraph, IRequest),
                provides=IJSONExporter)
class JSONContactParagraphExporter(JSONBaseParagraphExporter):
    """JSON contact paragraph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        lang = params.get('lang')
        self.get_attribute(result, 'name')
        self.get_i18n_attribute(result, 'charge', lang=lang)
        self.get_attribute(result, 'company')
        self.get_attribute(result, 'contact_email')
        self.get_attribute(result, 'phone_number')
        self.get_attribute(result, 'address')
        self.get_attribute(result, 'position', converter=lambda x: x.to_json())
        contact_form = get_reference_target(self.context.contact_form, request=self.request)
        if contact_form is not None:
            workflow = self.request.registry.queryMultiAdapter((contact_form, self.request),
                                                               IJSONExporter,
                                                               name='workflow')
            result['contact_form'] = {
                'title': II18n(contact_form).query_attribute('title', lang=lang),
                'absolute_url': absolute_url(contact_form, self.request),
                'canonical_url': canonical_url(contact_form, self.request),
                'workflow': workflow.to_json(**params)
            }
        self.get_image_attribute(result, 'photo', **params)
        return result
        