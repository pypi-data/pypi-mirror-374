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

from pyams_content.component.thesaurus import ICollectionsInfo, ICollectionsTarget, ITagsInfo, ITagsTarget, IThemesInfo, \
    IThemesTarget
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


class JSONThesaurusTargetExporter(JSONBaseExporter):
    """JSON thesaurus target exporter"""
    
    is_inner = True
    conversion_target = None
    
    terms_interface = None
    terms_attribute = None
    
    def convert_content(self, **params):
        result = []
        terms = self.terms_interface(self.context, None)
        if terms is not None:
            for term in (getattr(terms, self.terms_attribute) or ()):
                result.append({
                    'id': term.label,
                    'title': term.public_title
                })
        return result


@adapter_config(name='tags',
                required=(ITagsTarget, IRequest),
                provides=IJSONExporter)
class JSONTagsTargetExporter(JSONThesaurusTargetExporter):
    """JSON tags target exporter"""
    
    terms_interface = ITagsInfo
    terms_attribute = 'tags'


@adapter_config(name='themes',
                required=(IThemesTarget, IRequest),
                provides=IJSONExporter)
class JSONThemesTargetExporter(JSONThesaurusTargetExporter):
    """JSON themes target exporter"""
    
    terms_interface = IThemesInfo
    terms_attribute = 'themes'


@adapter_config(name='collections',
                required=(ICollectionsTarget, IRequest),
                provides=IJSONExporter)
class JSONCollectionsTargetExporter(JSONThesaurusTargetExporter):
    """JSON collections target exporter"""
    
    terms_interface = ICollectionsInfo
    terms_attribute = 'collections'
