#
# Copyright (c) 2015-2024 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_content.component.cards.skin.interfaces module

This module defines interfaces of Bootstrap cards paragraphs renderer settings.
"""

__docformat__ = 'restructuredtext'

from pyams_content.feature.renderer import IRendererSettings
from pyams_portal.portlets.cards.skin import ICardsPortletMasonryRendererSettings, ICardsPortletRendererSettings


class ICardsParagraphDefaultRendererSettings(ICardsPortletRendererSettings, IRendererSettings):
    """Cards paragraph default renderer settings"""


class ICardsParagraphMasonryRendererSettings(ICardsPortletMasonryRendererSettings, IRendererSettings):
    """Cards paragraph Masonry renderer settings"""
