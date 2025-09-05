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

"""PyAMS_content.shared.view.portlet.zmi module

This module defines previewer of view items portlet.
"""

from zope.interface import Interface

from pyams_content.shared.view.portlet import IViewItemsPortletSettings
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortletPreviewer
from pyams_portal.zmi import PortletPreviewer
from pyams_skin.interfaces.viewlet import IHelpViewletManager
from pyams_skin.viewlet.help import AlertMessage
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.form import IPropertiesEditForm

__docformat__ = 'restructuredtext'

from pyams_content import _


@viewlet_config(name='view-items-portlet-settings.warning',
                context=IViewItemsPortletSettings, layer=IAdminLayer, view=IPropertiesEditForm,
                manager=IHelpViewletManager, weight=20)
class ViewItemsPortletSettingsWarning(AlertMessage):
    """View items portlet settings warning message"""
    
    status = 'info'
    _message = _("WARNING: il you select multiple views and a renderer using aggregates, "
                 "results count and aggregates filters will be those of the first select view only!")


@adapter_config(required=(Interface, IPyAMSLayer, Interface, IViewItemsPortletSettings),
                provides=IPortletPreviewer)
@template_config(template='templates/view-preview.pt', layer=IPyAMSLayer)
class ViewItemsPortletPreviewer(PortletPreviewer):
    """View items portlet previewer"""
