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

"""PyAMS_content_api.shared.common.interfaces module

This module defines API related interfaces which are common to all shared contents.
"""

from zope.interface import Interface

__docformat__ = 'restructuredtext'


#
# Internal API routes
#
# These routes are used to access shared contents from internal API; they may require
# authentication, and can be used to create or update shared contents.
#

REST_CONTENT_INTERNAL_SEARCH_ROUTE = 'pyams_content.api.rest.internal.search'
REST_CONTENT_INTERNAL_SEARCH_ROUTE_SETTING = f'{REST_CONTENT_INTERNAL_SEARCH_ROUTE}_route.path'
REST_CONTENT_INTERNAL_SEARCH_PATH = '/api/content/rest/internal'

REST_CONTENT_INTERNAL_GETTER_ROUTE = 'pyams_content.api.rest.internal.getter'
REST_CONTENT_INTERNAL_GETTER_ROUTE_SETTING = f'{REST_CONTENT_INTERNAL_GETTER_ROUTE}_route.path'
REST_CONTENT_INTERNAL_GETTER_PATH = '/api/content/rest/{oid}/internal'


#
# Public API routes
#
# These routes are used to access shared contents from public API; they can require
# authentication, but are generally used to get information about published contents.
#

REST_CONTENT_PUBLIC_SEARCH_ROUTE = 'pyams_content.api.rest.public.search'
REST_CONTENT_PUBLIC_SEARCH_ROUTE_SETTING = f'{REST_CONTENT_PUBLIC_SEARCH_ROUTE}_route.path'
REST_CONTENT_PUBLIC_SEARCH_PATH = '/api/content/rest'

REST_CONTENT_PUBLIC_GETTER_ROUTE = 'pyams_content.api.rest.public.getter'
REST_CONTENT_PUBLIC_GETTER_ROUTE_SETTING = f'{REST_CONTENT_PUBLIC_GETTER_ROUTE}_route.path'
REST_CONTENT_PUBLIC_GETTER_PATH = '/api/content/rest/{oid}'


class IWfSharedContentCreator(Interface):
    """Shared content creator interface

    This interface is used to create shared contents from REST API.
    """


class IWfSharedContentFinder(Interface):
    """Shared content finder interface"""

    def find(self, params, request=None):
        """Find contents matching provided parameters

        This interface is generally used with shared tools to find contents.

        :param params: incoming parameters validated from incoming REST API request
        :param request: initial request object
        :return: an iterator over found contents
        """


class IWfSharedContentFinderParams(Interface):
    """Shared content finder parameters getter interface

    This interface is used via adapters to shared content finders to get
    query parameters.
    """

    def get_params(self, query, params, request=None, **kwargs):
        """Extend incoming query with elements extracted from provided parameters

        :param query: initial query object; may be a catalog query, or an Elasticsearch query
        :param params: incoming parameters validated from incoming REST API request
        :param request: initial request object
        :return: the incoming modified query
        """


class IWfSharedContentFinderFilter(Interface):
    """Shared content finder filter interface

    This interface is used via adapters to shared content finders to filter
    results after query execution.
    """

    def filter(self, results, params, request=None, **kwargs):
        """Filter incoming results

        :param results: initial results iterator
        :param params: incoming parameters validated from incoming REST API request
        :param request: initial request object
        :return: new iterator with filtered results
        """


class IContentAPIInfo(Interface):
    """Shared content API additional info"""
