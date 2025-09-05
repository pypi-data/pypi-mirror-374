#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_content_api.include module

This module is used for Pyramid integration.
"""

import re

from pyams_content_api.shared.common import REST_CONTENT_PUBLIC_GETTER_PATH, REST_CONTENT_PUBLIC_GETTER_ROUTE_SETTING
from pyams_content_api.shared.common.interfaces import REST_CONTENT_INTERNAL_GETTER_PATH, \
    REST_CONTENT_INTERNAL_GETTER_ROUTE, REST_CONTENT_INTERNAL_GETTER_ROUTE_SETTING, REST_CONTENT_INTERNAL_SEARCH_PATH, \
    REST_CONTENT_INTERNAL_SEARCH_ROUTE, REST_CONTENT_INTERNAL_SEARCH_ROUTE_SETTING, REST_CONTENT_PUBLIC_GETTER_ROUTE, \
    REST_CONTENT_PUBLIC_SEARCH_PATH, REST_CONTENT_PUBLIC_SEARCH_ROUTE, REST_CONTENT_PUBLIC_SEARCH_ROUTE_SETTING

__docformat__ = 'restructuredtext'


def include_package(config):
    """Pyramid package include"""
    
    # add translations
    config.add_translation_dirs('pyams_content_api:locales')
    
    # register REST API routes
    config.add_route(REST_CONTENT_INTERNAL_SEARCH_ROUTE,
                     config.registry.settings.get(REST_CONTENT_INTERNAL_SEARCH_ROUTE_SETTING,
                                                  REST_CONTENT_INTERNAL_SEARCH_PATH))
    
    config.add_route(REST_CONTENT_INTERNAL_GETTER_ROUTE,
                     config.registry.settings.get(REST_CONTENT_INTERNAL_GETTER_ROUTE_SETTING,
                                                  REST_CONTENT_INTERNAL_GETTER_PATH))
    
    config.add_route(REST_CONTENT_PUBLIC_SEARCH_ROUTE,
                     config.registry.settings.get(REST_CONTENT_PUBLIC_SEARCH_ROUTE_SETTING,
                                                  REST_CONTENT_PUBLIC_SEARCH_PATH))
    
    config.add_route(REST_CONTENT_PUBLIC_GETTER_ROUTE,
                     config.registry.settings.get(REST_CONTENT_PUBLIC_GETTER_ROUTE_SETTING,
                                                  REST_CONTENT_PUBLIC_GETTER_PATH))
    
    try:
        import pyams_zmi  # pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        config.scan(ignore=[re.compile(r'pyams_content_api\..*\.zmi\.?.*').search])
    else:
        config.scan()
