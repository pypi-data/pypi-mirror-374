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

"""PyAMS_content_api.shared.common.info module

This module defines base shared content information getter service.
"""

from colander import MappingSchema, drop
from cornice import Service
from cornice.validators import colander_validator
from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent, HTTPNotFound, HTTPOk

from pyams_content_api.feature.json import IJSONExporter
from pyams_content_api.shared.common.interfaces import REST_CONTENT_INTERNAL_GETTER_ROUTE
from pyams_content_api.shared.common.schema import BaseContentInfo, BaseContentSearchParams, ContentSearchParams
from pyams_layer.skin import apply_skin
from pyams_security.interfaces.base import USE_INTERNAL_API_PERMISSION
from pyams_security.rest import check_cors_origin, set_cors_headers
from pyams_sequence.reference import get_reference_target
from pyams_utils.rest import BaseResponseSchema, http_error, rest_responses
from pyams_workflow.interfaces import IWorkflowVersions, VersionError
from pyams_zmi.skin import AdminSkin

__docformat__ = 'restructuredtext'


info_service = Service(name=REST_CONTENT_INTERNAL_GETTER_ROUTE,
                       pyramid_route=REST_CONTENT_INTERNAL_GETTER_ROUTE,
                       description="PyAMS content base information service")


@info_service.options(validators=(check_cors_origin, set_cors_headers))
def info_options(request):
    """Content options endpoint"""
    return ''


class ContentInfoRequest(MappingSchema):
    """Content information request"""
    querystring = BaseContentSearchParams(missing=drop)
    
    
class ContentInfoResponse(BaseResponseSchema):
    """Content information schema"""
    info = BaseContentInfo(description="Content info",
                           missing=drop)


class ContentInfoResult(MappingSchema):
    """Content information response"""
    body = ContentInfoResponse()


info_get_responses = rest_responses.copy()
info_get_responses[HTTPOk.code] = ContentInfoResult(
    description="Base content information result")


@info_service.get(permission=USE_INTERNAL_API_PERMISSION,
                  schema=ContentInfoRequest(),
                  validators=(check_cors_origin, colander_validator, set_cors_headers),
                  response_schemas=info_get_responses)
def get_content_info(request):
    """Content information getter"""
    oid = request.matchdict['oid']
    if not oid:
        return http_error(request, HTTPBadRequest)
    apply_skin(request, AdminSkin)
    # check version ID
    version_id = None
    if '.' in oid:
        oid, version_id = oid.split('.', 1)
    target = get_reference_target(oid, request=request)
    if target is None:
        return http_error(request, HTTPNotFound)
    if version_id:
        versions = IWorkflowVersions(target, None)
        if versions is not None:
            try:
                target = versions.get_version(version_id)
            except VersionError:
                return http_error(request, HTTPNotFound)
    exporter = request.registry.queryMultiAdapter((target, request), IJSONExporter)
    if exporter is None:
        return http_error(request, HTTPNoContent)
    info = exporter.to_json(**request.validated.get('querystring', {}))
    return {
        'status': 'success',
        'info': info
    }
