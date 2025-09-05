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

"""PyAMS_content_api.shared.common.schema module

This module defines base content schemas.
"""

from colander import DateTime, Enum, Integer, MappingSchema, OneOf, SchemaNode, String, drop

from pyams_content.workflow import STATES_IDS
from pyams_content_api.component.illustration.schema import DisplayName

__docformat__ = 'restructuredtext'


class ContentDataType(MappingSchema):
    """Content data type schema"""
    name = SchemaNode(String(),
                      description="Data type name")
    label = SchemaNode(String(),
                       description="Data type label")


class BaseContentInfo(MappingSchema):
    """Base content information schema"""
    oid = SchemaNode(String(),
                     description="Content OID")
    title = SchemaNode(String(),
                       description="Content title")
    data_type = ContentDataType(description="Content data type",
                                missing=drop)


class SharedContentInfo(MappingSchema):
    """Shared content information schema"""
    oid = SchemaNode(String(),
                     description="Content unique ID")
    base_oid = SchemaNode(String(),
                          description="Content base OID")
    api_url = SchemaNode(String(),
                         description="REST API URL used to get full content information")
    public_url = SchemaNode(String(),
                            description="Canonical URL used to get access to content web page",
                            missing=drop)
    content_url = SchemaNode(String(),
                             description="String used to define content canonical URL",
                             missing=drop)
    title = SchemaNode(String(),
                       description="Content title")
    short_name = SchemaNode(String(),
                            description="Content short title",
                            missing=drop)
    header = SchemaNode(String(),
                        description="Content header",
                        missing=drop)
    description = SchemaNode(String(),
                             description="Content description",
                             missing=drop)


class WorkflowPublicationInfo(MappingSchema):
    """Workflow publication information schema"""
    state = SchemaNode(String(),
                       description="Workflow publication state",
                       validator=OneOf(STATES_IDS),
                       missing=drop)
    version = SchemaNode(Integer(),
                         description="Workflow version number",
                         missing=drop)
    publication_date = SchemaNode(DateTime(),
                                  description="First publication datetime in iso8601 format, including timezone",
                                  missing=drop)
    expiration_date = SchemaNode(DateTime(),
                                 description="Publication expiration datetime in iso8601 format, including timezone",
                                 missing=drop)


class BaseContentSearchParams(MappingSchema):
    """Base content search params schema"""
    lang = SchemaNode(String(),
                      description="Requested language for translated strings",
                      missing=drop)
    display_name = SchemaNode(Enum(DisplayName),
                              description="Images display name",
                              missing=drop)
    display_size = SchemaNode(String(),
                              description="Images display size, in pixels; syntax is 'w640' to specify width, "
                                          "'h480' to specify height or '640x480' to specify both",
                              missing=drop)
    included = SchemaNode(String(),
                          description="Comma separated list of extensions to include into JSON results output",
                          missing=drop)
    excluded = SchemaNode(String(),
                          description="Comma separated list of extensions to exclude from JSON results output",
                          missing=drop)


class ContentSearchParams(BaseContentSearchParams):
    """Content search params schema"""
    data_type = SchemaNode(String(),
                           description="Comma separated list of content data types to select",
                           missing=drop)
    age_limit = SchemaNode(Integer(),
                           description="Maximum days since content publication date",
                           missing=drop)
