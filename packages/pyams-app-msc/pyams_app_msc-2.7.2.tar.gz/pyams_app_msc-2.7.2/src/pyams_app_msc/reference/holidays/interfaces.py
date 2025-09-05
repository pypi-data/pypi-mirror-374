# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from zope.container.constraints import containers, contains
from zope.interface import Attribute, Interface
from zope.schema import Date, Int, TextLine

from pyams_content.reference.interfaces import IReferenceInfo, IReferenceTable

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


HOLIDAY_LOCATIONS_VOCABULARY = 'msc.holiday_locations'
'''Holiday locations vocabulary name'''


HOLIDAY_YEARS_VOCABULARY = 'msc.holiday_years'
'''Holiday years vocabulary name'''


HOLIDAY_POPULATIONS_VOCABULARY = 'msc.holiday_populations'
'''Holiday populations vocabulary name'''


class IHolidayPeriod(IReferenceInfo):
    """Holiday period interface"""
    
    containers('.IHolidayPeriodTable')
    
    description = TextLine(title=_("Period description"),
                           required=True)
    
    annee_scolaire = TextLine(title=_("Period scholar year"),
                              required=True)
    
    start_date = Date(title=_("Period start date"),
                      required=True)
    
    end_date = Date(title=_("Period end date"),
                    required=True)

    zones = TextLine(title=_("Period zones"),
                     required=False)
    
    location = TextLine(title=_("Period location"),
                        required=True)
    
    
class IHolidayPeriodTable(IReferenceTable):
    """Holiday period table interface"""
    
    contains(IHolidayPeriod)

    locations = Attribute("Holiday zones locations")
    
    def add_period(self, period):
        """Add a new period to the holiday periods table"""
        
    def add_period_ref(self, period):
        """Add a new reference to provided period properties"""

    def remove_period_ref(self, period):
        """Remove reference from provided period properties"""

    def drop_periods(self, scholar_year):
        """Drop all periods for provided scholar year"""

    def get_periods(self, location, scholar_year):
        """Get periods for provided location and scholar year"""
        

HOLIDAY_PERIODS_GETTER_SETTINGS_KEY = 'pyams_app_msc.holiday_periods_getter_settings'


class IHolidayPeriodsGetterSettings(Interface):
    """Holiday periods getter settings interface"""
    
    remote_url = TextLine(title=_("Holiday periods API URL"),
                          required=True,
                          default='https://data.education.gouv.fr/api/explore/v2.0/catalog/datasets/{dataset_id}/{action_id}')
    
    dataset_id = TextLine(title=_("Holiday periods API dataset ID"),
                          required=True,
                          default='fr-en-calendrier-scolaire')
    
    records_action_id = TextLine(title=_("Records API action ID"),
                                 required=True,
                                 default='records')

    condition_argument_name = TextLine(title=_("Records API condition argument name"),
                                       required=True,
                                       default='where')
    
    groupby_argument_name = TextLine(title=_("Records API group-by argument name"),
                                     required=True,
                                     default='group_by')
    
    period_argument_name = TextLine(title=_("Records API period argument name"),
                                    required=True,
                                    default='annee_scolaire')

    population_argument_name = TextLine(title=_("Records API population argument name"),
                                        required=True,
                                        default='population')
    
    limit_argument_name = TextLine(title=_("Records API limit argument name"),
                                   required=True,
                                   default='limit')
    
    offset_argument_name = TextLine(title=_("Records API offset argument name"),
                                    required=True,
                                    default='offset')
    
    default_page_size = Int(title=_("Records API default page size"),
                            required=True,
                            default=100)


class IHolidayPeriodsGetterService(Interface):
    """Holiday periods getter service interface"""
    
    def get_years(self):
        """Get holiday years from remote API"""
        
    def get_populations(self):
        """Get holiday populations from remote API"""
        
    def get_periods(self, **params):
        """Get holiday periods from remote API"""
