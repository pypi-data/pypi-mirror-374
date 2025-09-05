# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from zope.annotation.interfaces import IAttributeAnnotatable
from zope.container.constraints import containers, contains
from zope.container.interfaces import IContainer
from zope.interface import Interface
from zope.schema import Bool, TextLine, Date

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


class IClosurePeriod(IAttributeAnnotatable):
    """Closure period interface"""

    containers('.IClosurePeriodContainer')
    
    active = Bool(title=_("Active period"),
                  description=_("An inactive period is not displayed into theater planning"),
                  required=True,
                  default=True)
    
    label = TextLine(title=_("Label"),
                     description=_("Period label"),
                     required=True)
    
    start_date = Date(title=_("Period start date"),
                      required=True)
    
    end_date = Date(title=_("Period end date"),
                    required=True)
    
    
CLOSURE_PERIOD_CONTAINER_KEY = 'msc.closure.container'


class IClosurePeriodContainer(IContainer):
    """Closure period container interface"""
    
    contains(IClosurePeriod)

    def append(self, item):
        """Add period to container"""
        
    def get_active_periods(self, start_date, end_date):
        """Get periods overriding provided dates"""


class IClosurePeriodContainerTarget(Interface):
    """Closure period container target marker interface"""
