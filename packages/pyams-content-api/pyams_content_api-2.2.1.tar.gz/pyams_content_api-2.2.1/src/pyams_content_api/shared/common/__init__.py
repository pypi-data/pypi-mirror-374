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

"""PyAMS_content_api.shared.common module

This module defines base JSON shared content exporter.
"""

from pyramid.interfaces import IRequest

from pyams_content.shared.common.interfaces import IWfSharedContent
from pyams_content.shared.common.interfaces.types import IDataType, IWfTypedSharedContent
from pyams_content_api.feature.json import JSONBaseExporter
from pyams_content_api.feature.json.interfaces import IJSONExporter
from pyams_content_api.shared.common.interfaces import REST_CONTENT_INTERNAL_GETTER_PATH, \
    REST_CONTENT_INTERNAL_GETTER_ROUTE_SETTING, REST_CONTENT_PUBLIC_GETTER_PATH, \
    REST_CONTENT_PUBLIC_GETTER_ROUTE_SETTING
from pyams_layer.interfaces import ISkin
from pyams_layer.skin import apply_skin
from pyams_sequence.interfaces import ISequentialIdInfo
from pyams_utils.adapter import adapter_config
from pyams_utils.registry import query_utility
from pyams_utils.request import copy_request
from pyams_utils.url import absolute_url, canonical_url

__docformat__ = 'restructuredtext'


@adapter_config(required=(IWfSharedContent, IRequest),
                provides=IJSONExporter)
class JSONSharedContentExporter(JSONBaseExporter):
    """Default shared content JSON exporter"""

    getter_route_setting = REST_CONTENT_PUBLIC_GETTER_ROUTE_SETTING
    getter_route_default = REST_CONTENT_PUBLIC_GETTER_PATH
    
    internal_route_setting = REST_CONTENT_INTERNAL_GETTER_ROUTE_SETTING
    internal_route_default = REST_CONTENT_INTERNAL_GETTER_PATH

    def convert_content(self, **params):
        """Base context converter"""
        result = super().convert_content(**params)
        context = self.context
        lang = params.get('lang')
        sequence = ISequentialIdInfo(context)
        result['oid'] = sequence.hex_oid
        result['base_oid'] = sequence.get_base_oid().strip()
        getter_route = self.request.registry.settings.get(self.getter_route_setting,
                                                          self.getter_route_default)
        result['public_api_url'] = getter_route.format(content_type=self.context.content_type,
                                                       oid=sequence.hex_oid)
        internal_route = self.request.registry.settings.get(self.internal_route_setting,
                                                            self.internal_route_default)
        result['internal_api_url'] = internal_route.format(content_type=self.context.content_type,
                                                           oid=sequence.hex_oid)
        result['absolute_url'] = absolute_url(context, self.request)
        default_skin = query_utility(ISkin, name='PyAMS default skin')
        if default_skin is not None:
            public_request = copy_request(self.request)
            apply_skin(public_request, default_skin)
            result['canonical_url'] = canonical_url(context, public_request)
        self.get_i18n_attribute(result, 'title', lang)
        if context.handle_short_name:
            self.get_i18n_attribute(result, 'short_name', lang)
        if context.handle_content_url:
            self.get_attribute(result, 'content_url', name='content_path')
        if context.handle_header:
            self.get_i18n_attribute(result, 'header', lang)
        if context.handle_description:
            self.get_i18n_attribute(result, 'description', lang)
        return result


@adapter_config(required=(IWfTypedSharedContent, IRequest),
                provides=IJSONExporter)
class JSONTypedSharedContentExporter(JSONSharedContentExporter):
    """Typed shared content JSON exporter"""

    def convert_content(self, **params):
        """Base context converter"""
        result = super().convert_content(**params)
        self.get_data_attribute(result, 'data_type', getter=lambda x, y: x.get_data_type(),
                                **params)
        return result


@adapter_config(required=(IDataType, IRequest),
                provides=IJSONExporter)
class JSONDataTypeExporter(JSONBaseExporter):
    """JSON data type exporter"""
    
    def convert_content(self, **params):
        result = {}
        lang = params.get('lang')
        self.get_attribute(result, '__name__', name='id')
        self.get_i18n_attribute(result, 'label', lang=lang)
        folder = self.context.get_source_folder()
        if folder is not None:
            source = {}
            self.get_i18n_attribute(source, 'title', lang=lang, context=folder)
            source['absolute_url'] = absolute_url(folder, self.request)
            source['canonical_url'] = canonical_url(folder, self.request)
            result['source'] = source
        self.get_i18n_attribute(result, 'navigation_label', lang=lang)
        self.get_i18n_attribute(result, 'facets_label', lang=lang)
        self.get_i18n_attribute(result, 'facets_type_label', lang=lang)
        self.get_i18n_attribute(result, 'dashboard_label', lang=lang)
        self.get_attribute(result, 'display_as_tag')
        self.get_attribute(result, 'color')
        self.get_data_attribute(result, 'pictogram', **params)
        status = {}
        self.get_data_attribute(status, 'pictogram_on', name='on', **params)
        self.get_data_attribute(status, 'pictogram_off', name='off', **params)
        if status:
            result['status'] = status
        return result
    