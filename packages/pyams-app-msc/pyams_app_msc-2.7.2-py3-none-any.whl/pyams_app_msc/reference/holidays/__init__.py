# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

import locale
from datetime import date, datetime, timedelta

from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from pyramid.events import subscriber
from pyramid.interfaces import IRequest
from zope.component.interfaces import ISite
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_app_msc.reference.holidays.interfaces import HOLIDAY_LOCATIONS_VOCABULARY, HOLIDAY_POPULATIONS_VOCABULARY, \
    HOLIDAY_YEARS_VOCABULARY, IHolidayPeriod, IHolidayPeriodTable, IHolidayPeriodsGetterService
from pyams_content.reference import ReferenceInfo, ReferenceTable
from pyams_content_api.feature.json import IJSONExporter, JSONBaseExporter
from pyams_utils.adapter import adapter_config
from pyams_utils.factory import create_object, factory_config
from pyams_utils.interfaces.intids import IUniqueID
from pyams_utils.registry import query_utility
from pyams_utils.traversing import get_parent
from pyams_utils.vocabulary import vocabulary_config

__docformat__ = 'restructuredtext'


@factory_config(IHolidayPeriodTable)
class HolidayPeriodTable(ReferenceTable):
    """Holiday period table"""
    
    def __init__(self):
        super().__init__()
        self.locations = PersistentMapping()
    
    def add_period(self, period):
        locate(period, self)
        oid = IUniqueID(period).oid
        self[oid] = period
        self.add_period_ref(period)
        
    def add_period_ref(self, period):
        periods = self.locations.setdefault(period.location, PersistentMapping()) \
            .setdefault(period.annee_scolaire, PersistentList())
        if period.__name__ not in periods:
            periods.append(period.__name__)
    
    def remove_period_ref(self, period):
        if isinstance(period, str):
            period = self.get(period)
        locations = self.locations
        location = period.location
        annee_scolaire = period.annee_scolaire
        periods_names = locations[location][annee_scolaire]
        if period.__name__ in periods_names:
            periods_names.remove(period.__name__)
        if not periods_names:
            del locations[location][annee_scolaire]
        if not locations[location]:
            del locations[location]
    
    def drop_periods(self, scholar_year):
        for location, scholar_years in self.locations.copy().items():
            for period_name in scholar_years.get(scholar_year, []).copy():
                del self[period_name]

    def get_periods(self, location, start_date, end_date):
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        for scholar_year in self.locations.get(location, {}).values():
            for period_name in scholar_year:
                period = self.get(period_name)
                if (period is not None) and \
                        period.overlaps(start_date, end_date):
                    yield period
        

@subscriber(IObjectAddedEvent, context_selector=IHolidayPeriodTable)
def handle_added_holiday_period_table(event):
    """Register a new holiday table"""
    site = get_parent(event.object, ISite)
    registry = site.getSiteManager()
    if registry is not None:
        registry.registerUtility(event.object, IHolidayPeriodTable)


@factory_config(IHolidayPeriod)
class HolidayPeriod(ReferenceInfo):
    """Holiday period persistent class"""
    
    description = FieldProperty(IHolidayPeriod['description'])
    annee_scolaire = FieldProperty(IHolidayPeriod['annee_scolaire'])
    start_date = FieldProperty(IHolidayPeriod['start_date'])
    end_date = FieldProperty(IHolidayPeriod['end_date'])
    zones = FieldProperty(IHolidayPeriod['zones'])
    location = FieldProperty(IHolidayPeriod['location'])
    
    def __init__(self, **values):
        for key, value in values.items():
            if key in ('start_date', 'end_date'):
                if isinstance(value, str):
                    value = datetime.fromisoformat(value).date()
                elif isinstance(value, datetime):
                    value = value.date()
            setattr(self, key, value)
            
    def update(self, other: IHolidayPeriod):
        """Update a holiday period from another one"""
        for key in ('description', 'annee_scolaire', 'start_date', 'end_date',
                    'zones', 'location'):
            setattr(self, key, getattr(other, key))
    
    def __contains__(self, date):
        if isinstance(date, datetime):
            date = date.date()
        return self.start_date <= date <= self.end_date
    
    def overlaps(self, start_date, end_date):
        """Check if two holiday periods overlap"""
        return (self.start_date <= end_date) and (start_date <= self.end_date)
    
    
@subscriber(IObjectAddedEvent, context_selector=IHolidayPeriod)
def handle_added_holiday_period(event):
    """Handle a new holiday period"""
    period = event.object
    periods_table = get_parent(period, IHolidayPeriodTable)
    periods_table.add_period_ref(period)
    
    
@subscriber(IObjectRemovedEvent, context_selector=IHolidayPeriod)
def handle_removed_holiday_period(event):
    """Handle a removed holiday period"""
    period = event.object
    periods_table = get_parent(period, IHolidayPeriodTable)
    periods_table.remove_period_ref(period)
    
    
@adapter_config(required=(IHolidayPeriod, IRequest),
                provides=IJSONExporter)
class HolidayPeriodJSONExporter(JSONBaseExporter):
    """Holiday period JSON exporter"""
    
    conversion_target = None
    
    def convert_content(self, **params):
        
        def add_day(context, attr):
            return getattr(context, attr) + timedelta(days=1)
        
        result = super().convert_content(**params)
        self.get_attribute(result, 'description', 'title')
        self.get_attribute(result, 'start_date', 'start',
                           getter=add_day, converter=date.isoformat)
        self.get_attribute(result, 'end_date', 'end',
                           getter=add_day, converter=date.isoformat)
        result['display'] = 'background'
        result['contextMenu'] = False
        return result

    
@vocabulary_config(name=HOLIDAY_LOCATIONS_VOCABULARY)
class HolidayLocationsVocabulary(SimpleVocabulary):
    """Holiday locations vocabulary"""
    
    def __init__(self, context=None):
        table = query_utility(IHolidayPeriodTable)
        if table is not None:
            terms = sorted([
                SimpleTerm(v, title=v)
                for v in table.locations.keys()
            ], key=lambda t: locale.strxfrm(t.title))
        else:
            terms = []
        super().__init__(terms)
    
    
@vocabulary_config(name=HOLIDAY_YEARS_VOCABULARY)
class HolidayYearsVocabulary(SimpleVocabulary):
    """Holiday periods vocabulary"""
    
    def __init__(self, context=None):
        service = create_object(IHolidayPeriodsGetterService)
        if service is not None:
            terms = sorted([
                SimpleTerm(v, title=v)
                for v in service.get_years()
            ], key=lambda x: x.title, reverse=True)
        else:
            terms = []
        super().__init__(terms)


@vocabulary_config(name=HOLIDAY_POPULATIONS_VOCABULARY)
class HolidayPopulationsVocabulary(SimpleVocabulary):
    """Holiday populations vocabulary"""
    
    def __init__(self, context=None):
        service = create_object(IHolidayPeriodsGetterService)
        if service is not None:
            terms = sorted([
                SimpleTerm(v, title=v)
                for v in service.get_populations()
            ], key=lambda x: x.title)
        else:
            terms = []
        super().__init__(terms)
