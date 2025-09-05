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

"""PyAMS_content_api.feature.json.interfaces module

This module defines interfaces related to JSON conversion.
"""

from zope.interface import Attribute, Interface


__docformat__ = 'restructuredtext'


class IJSONExporter(Interface):
    """JSON exporter interface

    Multi-adapters providing this interface should require a context and a request.
    """

    is_inner = Attribute("Boolean attribute which defines if exported result should be "
                         "merged with other parent export, or included as a sub-object "
                         "using adapter name as key")

    def to_json(self, **params):
        """Convert adapted object to JSON

        :param params: JSON export settings; generally contains arguments
            extracted from REST API validation, to define requested JSON
            export parameters
        """
