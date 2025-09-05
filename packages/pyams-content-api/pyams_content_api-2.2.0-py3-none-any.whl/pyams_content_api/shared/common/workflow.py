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

"""PyAMS_content_api.shared.common.workflow module

This module defines adapters for JSON workflow information output.
"""

from pyramid.interfaces import IRequest
from zope.dublincore.interfaces import IZopeDublinCore

from pyams_content.shared.common.interfaces import IWfSharedContent
from pyams_content_api.feature.json import JSONBaseExporter
from pyams_content_api.feature.json.interfaces import IJSONExporter
from pyams_security.utility import get_principal
from pyams_utils.adapter import adapter_config
from pyams_utils.timezone import tztime
from pyams_workflow.interfaces import IWorkflowPublicationInfo, IWorkflowState

__docformat__ = 'restructuredtext'


@adapter_config(name='workflow',
                required=(IWfSharedContent, IRequest),
                provides=IJSONExporter)
class JSONSharedContentWorkflowExporter(JSONBaseExporter):
    """JSON shared content workflow exporter"""

    is_inner = True
    conversion_target = None

    def convert_content(self, **params):
        """JSON workflow conversion"""
        result = super().convert_content(**params)
        dc = IZopeDublinCore(self.context, None)
        if dc is not None:
            result['creation_date'] = dc.created.isoformat()
            result['modification_date'] = dc.modified.isoformat()
        state = IWorkflowState(self.context, None)
        if state is not None:
            result['version'] = state.version_id
            result['state'] = state.state
        pub_info = IWorkflowPublicationInfo(self.context, None)
        if pub_info is not None:
            if pub_info.publication_date:
                result['publication_date'] = tztime(pub_info.publication_date).isoformat()
                if pub_info.publisher:
                    principal = get_principal(principal_id=pub_info.publisher)
                    result['publisher'] = {
                        'id': principal.id,
                        'name': principal.title
                    }
                if pub_info.first_publication_date:
                    result['first_publication_date'] = tztime(pub_info.first_publication_date).isoformat()
                    result['content_publication_date'] = tztime(pub_info.content_publication_date).isoformat()
                if pub_info.publication_effective_date:
                    result['publication_effective_date'] = tztime(pub_info.publication_effective_date).isoformat()
                    result['visible_date'] = tztime(pub_info.visible_publication_date).isoformat()
                if pub_info.push_end_date:
                    result['push_end_date'] = tztime(pub_info.push_end_date).isoformat()
                if pub_info.publication_expiration_date:
                    result['expiration_date'] = tztime(pub_info.publication_expiration_date).isoformat()
        return result
