# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

import requests
from persistent import Persistent
from zope.schema.fieldproperty import FieldProperty

from pyams_app_msc.reference.holidays.interfaces import HOLIDAY_PERIODS_GETTER_SETTINGS_KEY, \
    IHolidayPeriod, IHolidayPeriodTable, IHolidayPeriodsGetterService, IHolidayPeriodsGetterSettings
from pyams_utils.adapter import adapter_config, get_annotation_adapter
from pyams_utils.dict import DotDict
from pyams_utils.factory import create_object, factory_config
from pyams_utils.registry import LOGGER, get_utility

__docformat__ = 'restructuredtext'


@factory_config(IHolidayPeriodsGetterSettings)
class HolidayPeriodsGetterSettings(Persistent):
    """Holiday periods getter API settings"""
    
    remote_url = FieldProperty(IHolidayPeriodsGetterSettings['remote_url'])
    dataset_id = FieldProperty(IHolidayPeriodsGetterSettings['dataset_id'])
    records_action_id = FieldProperty(IHolidayPeriodsGetterSettings['records_action_id'])
    condition_argument_name = FieldProperty(IHolidayPeriodsGetterSettings['condition_argument_name'])
    groupby_argument_name = FieldProperty(IHolidayPeriodsGetterSettings['groupby_argument_name'])
    period_argument_name = FieldProperty(IHolidayPeriodsGetterSettings['period_argument_name'])
    population_argument_name = FieldProperty(IHolidayPeriodsGetterSettings['population_argument_name'])
    limit_argument_name = FieldProperty(IHolidayPeriodsGetterSettings['limit_argument_name'])
    offset_argument_name = FieldProperty(IHolidayPeriodsGetterSettings['offset_argument_name'])
    default_page_size = FieldProperty(IHolidayPeriodsGetterSettings['default_page_size'])


@adapter_config(required=IHolidayPeriodTable,
                provides=IHolidayPeriodsGetterSettings)
def holiday_periods_getter_settings(context):
    """Holiday periods getter settings adapter"""
    return get_annotation_adapter(context, HOLIDAY_PERIODS_GETTER_SETTINGS_KEY,
                                  IHolidayPeriodsGetterSettings)


@factory_config(IHolidayPeriodsGetterService)
class HolidayPeriodsGetterService:
    """Holiday periods getter service"""
    
    def get_years(self):
        periods_table = get_utility(IHolidayPeriodTable)
        if periods_table is None:
            return
        settings = IHolidayPeriodsGetterSettings(periods_table, None)
        if settings is None:
            raise ValueError("Can't get holiday periods getter API service settings")
        offset = 0
        page_size = settings.default_page_size
        results = []
        while True:
            response = requests.get(settings.remote_url.format(
                dataset_id=settings.dataset_id,
                action_id=settings.records_action_id
            ), params={
                settings.offset_argument_name: page_size * offset,
                settings.limit_argument_name: page_size,
                settings.groupby_argument_name: settings.period_argument_name
            })
            if response.status_code != 200:
                break
            data = DotDict(response.json())
            if not data.records:
                break
            for record in data.records:
                results.append(record.record.fields[settings.period_argument_name])
            offset += 1
        return results
    
    def get_populations(self):
        periods_table = get_utility(IHolidayPeriodTable)
        if periods_table is None:
            return
        settings = IHolidayPeriodsGetterSettings(periods_table, None)
        if settings is None:
            raise ValueError("Can't get holiday periods getter API service settings")
        offset = 0
        page_size = settings.default_page_size
        results = []
        while True:
            response = requests.get(settings.remote_url.format(
                dataset_id=settings.dataset_id,
                action_id=settings.records_action_id
            ), params={
                settings.offset_argument_name: page_size * offset,
                settings.limit_argument_name: page_size,
                settings.groupby_argument_name: settings.population_argument_name
            })
            if response.status_code != 200:
                break
            data = DotDict(response.json())
            if not data.records:
                break
            for record in data.records:
                results.append(record.record.fields[settings.population_argument_name])
            offset += 1
        return results

    def get_periods(self, **params):
        periods_table = get_utility(IHolidayPeriodTable)
        if periods_table is None:
            return
        settings = IHolidayPeriodsGetterSettings(periods_table, None)
        if settings is None:
            raise ValueError("Can't get holiday periods getter API service settings")
        scholar_year = params.get('scholar_year')
        if not scholar_year:
            raise ValueError("Scholar year is required")
        periods_table.drop_periods(scholar_year)
        condition = f'{settings.period_argument_name}="{scholar_year}"'
        populations_condition = ' or '.join((
            f'{settings.population_argument_name}="{population}"'
            for population in params.get('populations', ())
        ))
        if populations_condition:
            condition = f'{condition} and ({populations_condition})'
        offset = 0
        nb_results = 0
        page_size = settings.default_page_size
        while True:
            response = requests.get(settings.remote_url.format(
                    dataset_id=settings.dataset_id,
                    action_id=settings.records_action_id
            ), params={
                settings.offset_argument_name: page_size * offset,
                settings.limit_argument_name: page_size,
                settings.condition_argument_name: condition
            })
            if response.status_code != 200:
                break
            data = DotDict(response.json())
            if not data.records:
                break
            LOGGER.debug(f"Loaded records: {len(data.records)}")
            for record in data.records:
                period_data = record.record.fields
                period = create_object(IHolidayPeriod, **period_data)
                if period is not None:
                    periods_table.add_period(period)
                    nb_results += 1
            offset += 1
        return nb_results
    