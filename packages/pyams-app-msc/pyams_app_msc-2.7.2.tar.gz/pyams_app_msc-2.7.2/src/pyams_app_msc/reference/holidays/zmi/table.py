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
from zope.interface import Interface, implementer

from pyams_app_msc.reference.holidays import IHolidayPeriodTable
from pyams_content.reference.zmi.table import ReferenceTableContainerTable, ReferenceTableNameColumn
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_table.interfaces import IColumn
from pyams_utils.adapter import adapter_config
from pyams_utils.date import format_date
from pyams_viewlet.manager import viewletmanager_config
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel
from pyams_zmi.interfaces.form import IFormTitle, IPropertiesEditForm
from pyams_zmi.interfaces.table import IColumnSortData
from pyams_zmi.interfaces.viewlet import IPropertiesMenu, ISiteManagementMenu
from pyams_zmi.table import TableAdminView
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


HOLIDAY_PERIOD_TABLE_LABEL = _("Holiday periods")


@adapter_config(required=(IHolidayPeriodTable, IPyAMSLayer, Interface),
                provides=IObjectLabel)
def holiday_period_table_label(context, request, view):
    """Holiday period table label adapter"""
    return request.localizer.translate(HOLIDAY_PERIOD_TABLE_LABEL)


@viewletmanager_config(name='contents.menu',
                       context=IHolidayPeriodTable, layer=IAdminLayer,
                       manager=ISiteManagementMenu, weight=10,
                       permission=VIEW_SYSTEM_PERMISSION,
                       provides=IPropertiesMenu)
class HolidayPeriodTableContentsMenu(NavigationMenuItem):
    """Holiday period table contents menu"""
    
    label = _("Table contents")
    icon_class = 'fas fa-table'
    href = '#contents.html'
    
    
class HolidayPeriodTableContainerTable(ReferenceTableContainerTable):
    """Holiday period table container table"""
    
    @reify
    def data_attributes(self):
        attributes = super().data_attributes
        attributes['table'].update({
            'data-ams-order': '0,asc'
        })
        return attributes
    
    
@adapter_config(name='name',
                required=(IHolidayPeriodTable, IAdminLayer, HolidayPeriodTableContainerTable),
                provides=IColumn)
class HolidayPeriodTableNameColumn(ReferenceTableNameColumn):
    """Holiday period table name column"""

    i18n_header = _("Location")
    attr_name = 'location'


@adapter_config(name='scholar-year',
                required=(IHolidayPeriodTable, IAdminLayer, HolidayPeriodTableContainerTable),
                provides=IColumn)
class HolidayPeriodTableScholarYearColumn(ReferenceTableNameColumn):
    """Holiday period table scholar year column"""

    i18n_header = _("Scolar year")
    attr_name = 'annee_scolaire'

    weight = 20


@adapter_config(name='zones',
                required=(IHolidayPeriodTable, IAdminLayer, HolidayPeriodTableContainerTable),
                provides=IColumn)
class HolidayPeriodTableZonesColumn(ReferenceTableNameColumn):
    """Holiday period table zones column"""

    i18n_header = _("Zones")
    attr_name = 'zones'

    weight = 30


@adapter_config(name='description',
                required=(IHolidayPeriodTable, IAdminLayer, HolidayPeriodTableContainerTable),
                provides=IColumn)
class HolidayPeriodTableDescriptionColumn(ReferenceTableNameColumn):
    """Holiday period table description column"""

    i18n_header = _("Description")
    attr_name = 'description'

    weight = 40


@adapter_config(name='start-date',
                required=(IHolidayPeriodTable, IAdminLayer, HolidayPeriodTableContainerTable),
                provides=IColumn)
@implementer(IColumnSortData)
class HolidayPeriodTableStartDateColumn(ReferenceTableNameColumn):
    """Holiday period table start date column"""

    i18n_header = _("Period start date")
    attr_name = 'start_date'

    weight = 50

    def get_value(self, obj):
        return format_date(getattr(obj, self.attr_name))

    @staticmethod
    def get_sort_value(obj):
        return obj.end_date.isoformat()


@adapter_config(name='end_date',
                required=(IHolidayPeriodTable, IAdminLayer, HolidayPeriodTableContainerTable),
                provides=IColumn)
@implementer(IColumnSortData)
class HolidayPeriodTableEndDateColumn(ReferenceTableNameColumn):
    """Holiday period table end date column"""

    i18n_header = _("Period end date")
    attr_name = 'end_date'

    weight = 60

    def get_value(self, obj):
        return format_date(getattr(obj, self.attr_name))

    @staticmethod
    def get_sort_value(obj):
        return obj.end_date.isoformat()
    
    
@pagelet_config(name='contents.html',
                context=IHolidayPeriodTable, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION)
class HolidayPeriodsTableContentsView(TableAdminView):
    """Holiday period table contents view"""
    
    title = _("Holiday periods")
    
    table_class = HolidayPeriodTableContainerTable
    table_label = _("Holiday periods list")


@adapter_config(required=(IHolidayPeriodTable, IAdminLayer, IPropertiesEditForm),
                provides=IFormTitle)
def holiday_periods_table_title(context, request, form):
    """Holiday period table edit form title getter"""
    translate = request.localizer.translate
    return translate(_("Holiday periods table"))
