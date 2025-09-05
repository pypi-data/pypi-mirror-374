# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from enum import Enum as BuiltinEnum

from colander import MappingSchema, SchemaNode, String, drop

__docformat__ = 'restructuredtext'


class BaseIllustrationInfo(MappingSchema):
    """Base illustration information schema"""
    title = SchemaNode(String(),
                       description="Illustration title",
                       missing=drop)
    alt_title = SchemaNode(String(),
                           description="Illustration alternate title",
                           missing=drop)
    author = SchemaNode(String(),
                        description="Illustration author",
                        missing=drop)
    src = SchemaNode(String(),
                     description="Illustration image source URL")
    
    
class IllustrationInfo(BaseIllustrationInfo):
    """Illustration information schema"""
    description = SchemaNode(String(),
                             description="Illustration description",
                             missing=drop)


class IllustrationParagraph(IllustrationInfo):
    """Illustration paragraph schema"""


class DisplayName(BuiltinEnum):
    """Image display enumeration"""
    xs = 'xs'
    sm = 'sm'
    md = 'md'
    lg = 'lg'
    xl = 'xl'
    portrait = 'portrait'
    square = 'square'
    pano = 'pano'
    card = 'card'
    banner = 'banner'
