# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from datetime import date, datetime, timedelta

from persistent import Persistent
from pyramid.interfaces import IRequest
from zope.container.btree import BTreeContainer
from zope.container.contained import Contained
from zope.interface import classImplements
from zope.location.interfaces import ISublocations
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.interfaces import ITraversable

from pyams_app_msc.feature.closure.interfaces import CLOSURE_PERIOD_CONTAINER_KEY, IClosurePeriod, \
    IClosurePeriodContainer, IClosurePeriodContainerTarget
from pyams_app_msc.interfaces import MANAGE_THEATER_PERMISSION
from pyams_app_msc.shared.theater import Theater
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_utils.adapter import ContextAdapter, adapter_config, get_annotation_adapter
from pyams_utils.container import SimpleContainerMixin
from pyams_utils.factory import factory_config

__docformat__ = 'restructuredtext'


classImplements(Theater, IClosurePeriodContainerTarget)


@factory_config(IClosurePeriod)
class ClosurePeriod(Persistent, Contained):
    """Closure period class"""

    active = FieldProperty(IClosurePeriod['active'])
    label = FieldProperty(IClosurePeriod['label'])
    start_date = FieldProperty(IClosurePeriod['start_date'])
    end_date = FieldProperty(IClosurePeriod['end_date'])

    def overlaps(self, start_date, end_date):
        return (self.start_date <= end_date) and (start_date <= self.end_date)


@adapter_config(required=IClosurePeriod,
                provides=IViewContextPermissionChecker)
class ClosurePeriodPermissionChecker(ContextAdapter):
    """Closure period permission checker"""

    edit_permission = MANAGE_THEATER_PERMISSION


@adapter_config(required=(IClosurePeriod, IRequest),
                provides=IJSONExporter)
class ClosurePeriodJSONExporter(JSONBaseExporter):
    """Closure period JSON exporter"""
    
    conversion_target = None
    
    def convert_content(self, **params):

        def add_day(context, attr):
            return getattr(context, attr) + timedelta(days=1)

        result = super().convert_content(**params)
        self.get_attribute(result, 'label', 'title')
        self.get_attribute(result, 'start_date', 'start',
                           converter=date.isoformat)
        self.get_attribute(result, 'end_date', 'end',
                           getter=add_day, converter=date.isoformat)
        result['display'] = 'background'
        result['textColor'] = 'var(--fc-nobookable-text)'
        result['backgroundColor'] = 'var(--fc-nobookable-bg)'
        result['borderColor'] = 'var(--fc-nobookable-border)'
        result['zIndex'] = 3
        result['opacity'] = 100
        result['contextMenu'] = False
        return result
        

@factory_config(IClosurePeriodContainer)
class ClosurePeriodContainer(SimpleContainerMixin, BTreeContainer):
    """Closure period container class"""

    def get_active_periods(self, start_date, end_date):
        """Get periods"""
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        for period in self.values():
            if period.active and period.overlaps(start_date, end_date):
                yield period


@adapter_config(required=IClosurePeriodContainerTarget,
                provides=IClosurePeriodContainer)
def closure_period_container_factory(context):
    """Closure period container factory"""
    return get_annotation_adapter(context, CLOSURE_PERIOD_CONTAINER_KEY,
                                  IClosurePeriodContainer,
                                  name='++closure++')


@adapter_config(name='closure',
                required=IClosurePeriodContainerTarget,
                provides=ITraversable)
class ClosurePeriodContainerTraverser(ContextAdapter):
    """Closure period container traverser"""

    def traverse(self, name, furtherPath=None):
        return IClosurePeriodContainer(self.context, None)


@adapter_config(name='closure',
                required=IClosurePeriodContainerTarget,
                provides=ISublocations)
class ClosurePeriodContainerSublocations(ContextAdapter):
    """Closure period container sublocations"""

    def sublocations(self):
        container = IClosurePeriodContainer(self.context, None)
        if container is not None:
            yield from container.values()
