# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from pyams_content.feature.alert import IAlertManagerInfo

__docformat__ = 'restructuredtext'


def evolve(site):
    """Evolve 1: update alerts manager views property"""
    alerts_manager = IAlertManagerInfo(site, None)
    if alerts_manager is not None:
        if hasattr(alerts_manager, 'context_view'):
            context_view = getattr(alerts_manager, 'context_view')
            if context_view is not None:
                alerts_manager.context_views = [context_view]
        delattr(alerts_manager, 'context_view')
        