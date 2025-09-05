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

"""PyAMS_content.feature.alert.interfaces module

"""

from zope.interface import Interface
from zope.schema import Choice

from pyams_content.shared.view import VIEW_CONTENT_TYPE
from pyams_content.shared.view.interfaces.query import MergeModes, VIEWS_MERGERS_VOCABULARY
from pyams_sequence.schema import InternalReferenceField, InternalReferencesListField

__docformat__ = 'restructuredtext'

from pyams_content import _


ALERT_MANAGER_KEY = 'pyams_content.alerts'


class IAlertManagerInfo(Interface):
    """Alert manager info interface"""

    reference = InternalReferenceField(title=_("Global alerts view"),
                                       description=_("Internal view target reference; please note that alerts "
                                                     "content type selection will be added automatically to "
                                                     "settings of the selected view"),
                                       content_type=VIEW_CONTENT_TYPE,
                                       required=False)

    context_views = InternalReferencesListField(title=_("Context alerts views"),
                                                description=_("Reference to the views used to get context alerts; please "
                                                              "note that alerts content type selection will be added "
                                                              "automatically to settings of the selected views"),
                                                content_type=VIEW_CONTENT_TYPE,
                                                required=False)
    
    context_views_merge_mode = Choice(title=_("Views merge mode"),
                                      description=_("If you select several views, you can select \"merge\" mode, which is "
                                                    "the way used to merge items from several views"),
                                      vocabulary=VIEWS_MERGERS_VOCABULARY,
                                      default=MergeModes.CONCAT.value,
                                      required=True)

    def get_global_alerts(self, request):
        """Iterator over global alerts"""

    def get_context_alerts(self, request, context=None):
        """Iterator over visible alerts associated with request context"""
