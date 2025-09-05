# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from pyramid.decorator import reify
from pyramid.view import view_config

from pyams_app_msc.feature.closure import IClosurePeriodContainer, IClosurePeriodContainerTarget
from pyams_app_msc.feature.closure.zmi import IClosurePeriodContainerTable
from pyams_app_msc.interfaces import MANAGE_THEATER_PERMISSION, VIEW_THEATER_PERMISSION
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_table.interfaces import IColumn, IValues
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.helper.container import delete_container_element, switch_element_attribute
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IPropertiesMenu
from pyams_zmi.table import AttributeSwitcherColumn, DateColumn, NameColumn, Table, TableAdminView, TrashColumn
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


@viewlet_config(name='closure-periods.menu',
                context=IClosurePeriodContainerTarget, layer=IAdminLayer,
                manager=IPropertiesMenu, weight=515,
                permission=VIEW_THEATER_PERMISSION)
class ClosurePeriodsMenu(NavigationMenuItem):
    """Closure periods menu"""
    
    label = _("Closure periods")
    href = '#closure-periods.html'
    
    
@factory_config(IClosurePeriodContainerTable)
class ClosurePeriodContainerTable(Table):
    """Closure period container table"""
    
    display_if_empty = True
    
    sort_on = 'table-start-date-2'
    sort_order = 'descending'
    
    @reify
    def data_attributes(self):
        attributes = super().data_attributes
        attributes.setdefault('table', {}).update({
            'data-ams-order': '2,desc'
        })
        return attributes
    
    
@adapter_config(required=(IClosurePeriodContainerTarget, IAdminLayer, IClosurePeriodContainerTable),
                provides=IValues)
class ClosurePeriodContainerTableValues(ContextRequestViewAdapter):
    """Closure period container table values adapter"""
    
    @property
    def values(self):
        """Closure period container table values getter"""
        yield from IClosurePeriodContainer(self.context).values()
        
        
@adapter_config(name='active',
                required=(IClosurePeriodContainerTarget, IAdminLayer, IClosurePeriodContainerTable),
                provides=IColumn)
class ClosurePeriodsActiveColumn(AttributeSwitcherColumn):
    """Closure periods table active column"""

    attribute_name = 'active'
    attribute_switcher = 'switch-active-closure-period.json'

    icon_off_class = 'far fa-eye-slash text-danger'

    permission = MANAGE_THEATER_PERMISSION
    weight = 1

    def get_icon_hint(self, item):
        """Icon hint getter"""
        if self.has_permission(item):
            hint = _("Click icon to switch period activity")
        elif item.active:
            hint = _("This period is active")
        else:
            hint = _("This period is not active")
        return self.request.localizer.translate(hint)


@view_config(name='switch-active-closure-period.json',
             context=IClosurePeriodContainerTarget, request_type=IPyAMSLayer,
             renderer='json', xhr=True)
def switch_active_closure_period(request):
    """Switch closure period activity flag"""
    return switch_element_attribute(request, container_factory=IClosurePeriodContainer)


@adapter_config(name='label',
                required=(IClosurePeriodContainerTarget, IAdminLayer, IClosurePeriodContainerTable),
                provides=IColumn)
class ClosurePeriodLabelColumn(NameColumn):
    """Closure period table label column"""

    attr_name = 'label'
    i18n_header = _("Period label")


@adapter_config(name='start-date',
                required=(IClosurePeriodContainerTarget, IAdminLayer, IClosurePeriodContainerTable),
                provides=IColumn)
class ClosurePeriodStartDateColumn(DateColumn):
    """Closure period table start date column"""
    
    header = _("Period start date")
    attr_name = 'start_date'
    
    weight = 20


@adapter_config(name='end-date',
                required=(IClosurePeriodContainerTarget, IAdminLayer, IClosurePeriodContainerTable),
                provides=IColumn)
class ClosurePeriodEndDateColumn(DateColumn):
    """Closure period table end date column"""
    
    header = _("Period end date")
    attr_name = 'end_date'
    
    weight = 30


@adapter_config(name='trash',
                required=(IClosurePeriodContainerTarget, IAdminLayer, IClosurePeriodContainerTable),
                provides=IColumn)
class ClosurePeriodTrashColumn(TrashColumn):
    """Closure period table trash column"""

    object_data = {
        'ams-modules': 'container',
        'ams-delete-target': 'delete-closure-period.json'
    }


@view_config(name='delete-closure-period.json',
             context=IClosurePeriodContainerTarget, request_type=IPyAMSLayer,
             renderer='json', xhr=True,
             permission=MANAGE_THEATER_PERMISSION)
def delete_closure_period(request):
    """Delete closure period"""
    return delete_container_element(request, container_factory=IClosurePeriodContainer)


@pagelet_config(name='closure-periods.html',
                context=IClosurePeriodContainerTarget, layer=IPyAMSLayer,
                permission=VIEW_THEATER_PERMISSION)
class ClosurePeriodsView(TableAdminView):
    """Closure periods view"""

    title = _("Closure periods")

    table_class = IClosurePeriodContainerTable
    table_label = _("Closure periods list")
