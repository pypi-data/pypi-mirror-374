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

from pyams_content.component.association import IAssociationContainer, IAssociationContainerTarget
from pyams_content.component.association.interfaces import IAssociationParagraph
from pyams_content_api.component.paragraph import JSONBaseParagraphExporter
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


def get_associations(context, request, **params):
    """Associations getter"""
    associations = []
    registry = request.registry
    container = IAssociationContainer(context)
    for association in container.get_visible_items(request):
        exporter = registry.queryMultiAdapter((association, request), IJSONExporter)
        if exporter is not None:
            output = exporter.to_json(**params)
            if output:
                associations.append(output)
    return associations

@adapter_config(name='associations',
                required=(IAssociationContainerTarget, IRequest),
                provides=IJSONExporter)
class JSONAssociationContainerTargetExporter(JSONBaseExporter):
    """JSON association container target exporter"""
    
    is_inner = True
    conversion_target = None
    
    def convert_content(self, **params):
        return get_associations(self.context, self.request, **params)

    
@adapter_config(required=(IAssociationParagraph, IRequest),
                provides=IJSONExporter)
class JSONAssociationParagraphExporter(JSONBaseParagraphExporter):
    """JSON association paragraph exporter"""
    
    def convert_content(self, **params):
        result = super().convert_content(**params)
        associations = get_associations(self.context, self.request, **params)
        if associations:
            result['associations'] = associations
        return result
        