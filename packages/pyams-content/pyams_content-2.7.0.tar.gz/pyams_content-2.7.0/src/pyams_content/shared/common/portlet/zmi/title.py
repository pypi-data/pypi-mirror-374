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

"""PyAMS_content.shared.common.portlet.zmi.title module

This module defines management components of shared contents title portlet.
"""

__docformat__ = 'restructuredtext'

from zope.interface import Interface

from pyams_content.shared.common.portlet.interfaces import ISharedContentTitlePortletSettings
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortletPreviewer
from pyams_portal.zmi import PortletPreviewer
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config


@adapter_config(required=(Interface, IPyAMSLayer, Interface, ISharedContentTitlePortletSettings),
                provides=IPortletPreviewer)
@template_config(template='templates/title-preview.pt', layer=IPyAMSLayer)
class SharedContentTitlePortletPreviewer(PortletPreviewer):
    """Shared content title portlet previewer"""
