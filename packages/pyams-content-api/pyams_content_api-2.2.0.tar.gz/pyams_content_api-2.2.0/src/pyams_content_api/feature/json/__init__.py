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

"""PyAMS_content_api.feature.json module

This module defines base JSON exporter class.
"""

from typing import Any, Callable, Iterable

from pyams_content_api.feature.json.interfaces import IJSONExporter
from pyams_file.interfaces.thumbnail import IThumbnails
from pyams_i18n.interfaces import II18n, INegotiator
from pyams_utils.adapter import ContextRequestAdapter
from pyams_utils.interfaces.text import IHTMLRenderer
from pyams_utils.registry import get_pyramid_registry, get_utility
from pyams_utils.url import absolute_url

__docformat__ = 'restructuredtext'


class JSONBaseExporter(ContextRequestAdapter):
    """JSON base exporter"""

    def to_json(self, **params):
        """JSON converter"""
        lang = params.get('lang')
        if not lang:
            negotiator = get_utility(INegotiator)
            params['lang'] = negotiator.server_language
        result = self.convert_content(**params)
        registry = get_pyramid_registry()
        target = self.conversion_target
        if target is None:
            return result
        for name, converter in registry.getAdapters((target, self.request), IJSONExporter):
            if not name:  # exclude this default adapter
                continue
            if (('included' in params) and (name not in params['included'].split(','))) or \
                    (('excluded' in params) and (name in params['excluded'].split(','))):
                continue
            output = converter.to_json(**params)
            if not output:
                continue
            if converter.is_inner:
                result.update({name: output})
            else:
                result.update(output)
        return result

    @property
    def conversion_target(self):
        """Conversion target getter"""
        return self.context

    def convert_content(self, **params):
        """Base context converter"""
        return {}

    def get_attribute(self,
                      result: dict,
                      attr: str = None,
                      name: str = None,
                      getter: Callable = None,
                      converter: Callable = None,
                      context: Any = None):
        """Get standard attribute

        :param result: dict to be updated in place with getter value
        :param attr: attribute name
        :param name: result attribute name; same as `attr` if None
        :param getter: custom attribute getter
        :param converter: custom value converter
        :param context: custom context on which getter is applied
        """
        if context is None:
            context = self.context
        if getter is None:
            getter = getattr
            if not hasattr(context, attr):
                return
        value = getter(context, attr)
        if value is not None:
            if name is None:
                name = attr
            if converter is not None:
                value = converter(value)
            result[name] = value

    def get_i18n_attribute(self,
                           result: dict,
                           attr: str,
                           lang: str,
                           name: str = None,
                           converter: Callable = None,
                           context: Any = None):
        """Get localized attribute

        :param result: dict to be updated in place with getter value
        :param attr: attribute name
        :param lang: language
        :param name: result attribute name; same as `attr` if None
        :param converter: custom value converter
        :param context: custom context on which getter is applied
        """
        if context is None:
            context = self.context
        if not hasattr(context, attr):
            return
        if name is None:
            name = attr
        if lang:
            value = II18n(context).query_attribute(attr, lang=lang)
            if converter is not None:
                value = converter(value)
            if value:
                result[name] = value

    def get_html_attribute(self,
                           result: dict,
                           attr: str,
                           lang: str,
                           name: str = None,
                           converter: Callable = None,
                           context: Any = None):
        """Get HTML attribute

        :param result: dict to be updated in place with getter value
        :param attr: attribute name
        :param lang: language
        :param name: result attribute name; same as `attr` if None
        :param converter: custom value converter
        :param context: custom context on which getter is applied
        """
        if context is None:
            context = self.context
        if not hasattr(context, attr):
            return
        if lang:
            value = II18n(context).query_attribute(attr, lang=lang)
            if value:
                if converter is None:
                    renderer = self.request.registry.queryMultiAdapter((value, self.request),
                                                                       IHTMLRenderer,
                                                                       name='oid_to_href')
                    if renderer is not None:
                        result[name or attr] = renderer.render()
                else:
                    result[name or attr] = converter(value)

    def get_list_attribute(self,
                           result: dict,
                           items: Iterable,
                           name: str = None,
                           **params):
        """Get inner list attribute

        :param result: dict to be updated in place with getter value
        :param items: iterable on which getter is applied
        :param name: attribute name in result
        :param params: additional params to apply on items JSON converter
        """
        registry = get_pyramid_registry()
        values = []
        for item in items:
            converter = registry.queryMultiAdapter((item, self.request), IJSONExporter)
            if converter is not None:
                value = converter.to_json(params)
                if value:
                    values.append(value)
        if values:
            result[name] = values

    def get_file_attribute(self,
                           result: dict,
                           attr: str,
                           name: str = None,
                           getter: Callable = None,
                           context: Any = None,
                           **params):
        """Get file URL on given context

        :param result: dict to be updated in place with getter value
        :param attr: attribute name
        :param getter: custom attribute getter
        :param context: custom context on which getter is applied
        :param params: incoming JSON converter params

        :return: file absolute URL
        """
        if context is None:
            context = self.context
        if getter is None:
            getter = getattr
            if not hasattr(context, attr):
                return
        file = getter(context, attr)
        if isinstance(file, dict):
            file = file.get(params.get('lang'))
        if not file:
            return
        result[name or attr] = {
            'src': absolute_url(file, self.request),
            'filename': file.filename,
            'content_type': file.content_type
        }

    def get_image_attribute(self,
                            result: dict,
                            attr: str,
                            name: str = None,
                            getter: Callable = None,
                            context: Any = None,
                            **params):
        """Get image URL on given context

        :param result: dict to be updated in place with getter value
        :param attr: attribute name
        :param name: name of attribute in result
        :param getter: custom attribute getter
        :param context: custom context on which getter is applied
        :param params: incoming JSON converter params

        :return: image absolute URL
        """

        from pyams_content_api.component.illustration.schema import DisplayName

        if context is None:
            context = self.context
        if getter is None:
            getter = getattr
            if not hasattr(context, attr):
                return
        image = getter(context, attr)
        if isinstance(image, dict):
            image = image.get(params.get('lang'))
        if not image:
            return
        thumbnails = IThumbnails(image, None)
        if thumbnails is not None:
            thumbnail = thumbnails.get_thumbnail(f"{params.get('display_name', DisplayName.md).value}:"
                                                 f"{params.get('display_size', '800x800')}")
            result[name or attr] = {
                'src': absolute_url(thumbnail, self.request),
                'filename': image.filename,
                'content_type': thumbnail.content_type
            }
        else:
            result[name or attr] = {
                'src': absolute_url(image, self.request),
                'filename': image.filename,
                'content_type': image.content_type
            }

    def get_data_attribute(self,
                           result: dict,
                           attr: str,
                           name: str = None,
                           getter: Callable = None,
                           context: Any = None,
                           **params):
        """Get data attribute on given context
        
        This data attribute is converted to JSON using an adapted JSON exporter.
        
        :param result: dict to be updated in place with getter value
        :param attr: source attribute name
        :param name: name of attribute in result
        :param getter: custom attribute getter
        :param context: custom context on which getter is applied
        """
        if context is None:
            context = self.context
        if getter is None:
            getter = getattr
            if not hasattr(context, attr):
                return
        value = getter(context, attr)
        if value or (value is False):
            if name is None:
                name = attr
            exporter = self.request.registry.queryMultiAdapter((value, self.request),
                                                               IJSONExporter)
            if exporter is not None:
                result[name] = exporter.to_json(**params)
