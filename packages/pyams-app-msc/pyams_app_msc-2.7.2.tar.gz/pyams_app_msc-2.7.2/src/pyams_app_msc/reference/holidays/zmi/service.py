# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from zope.interface import Interface
from zope.schema import Choice, List

from pyams_app_msc.reference.holidays import HOLIDAY_YEARS_VOCABULARY, IHolidayPeriodsGetterService
from pyams_app_msc.reference.holidays.interfaces import HOLIDAY_POPULATIONS_VOCABULARY, IHolidayPeriodTable, \
    IHolidayPeriodsGetterSettings
from pyams_app_msc.reference.holidays.zmi.table import HolidayPeriodTableContainerTable
from pyams_content.interfaces import MANAGE_TOOL_PERMISSION
from pyams_form.ajax import ajax_form_config
from pyams_form.button import Buttons, handler
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer, IFormContent, IGroup
from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.schema.button import CloseButton, SubmitButton
from pyams_skin.viewlet.menu import MenuItem
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.factory import create_object
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalAddForm, FormGroupSwitcher
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.form import IPropertiesEditForm
from pyams_zmi.interfaces.viewlet import IContextActionsDropdownMenu

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


#
# Service settings edit form
#

@adapter_config(name='holidays-service-settings',
                required=(IHolidayPeriodTable, IAdminLayer, IPropertiesEditForm),
                provides=IGroup)
class HolidayPeriodsServiceSettingsGroup(FormGroupSwitcher):
    """Holidays periods service settings group"""
    
    legend = _("Holidays service settings")
    fields = Fields(IHolidayPeriodsGetterSettings)
    
    weight = 10


@adapter_config(required=(IHolidayPeriodTable, IAdminLayer, HolidayPeriodsServiceSettingsGroup),
                provides=IFormContent)
def holiday_periods_service_settings_content(context, request, form):
    """Holidays periods service settings content adapter"""
    return IHolidayPeriodsGetterSettings(context)


#
# Holiday periods service getter
#

@viewlet_config(name='holidays-service-caller.menu',
                context=IHolidayPeriodTable, layer=IAdminLayer, view=HolidayPeriodTableContainerTable,
                manager=IContextActionsDropdownMenu, weight=10,
                permission=MANAGE_TOOL_PERMISSION)
class HolidayPeriodsServiceMenu(MenuItem):
    """Holidays periods service caller menu"""
    
    label = _("Get new periods...")
    icon_class = 'fas fa-download'

    href = 'download-periods.html'
    modal_target = True
    
    
class IHolidayPeriodsServiceCallerFields(Interface):
    """Holiday periods service caller fields interface"""
    
    scholar_year = Choice(title=_("Scholar year"),
                          description=_("Scholar year used to get holiday periods"),
                          vocabulary=HOLIDAY_YEARS_VOCABULARY)

    populations = List(title=_("Populations"),
                       description=_("Populations selected to get holiday periods"),
                       value_type=Choice(vocabulary=HOLIDAY_POPULATIONS_VOCABULARY),
                       required=False)
    

class IHolidayPeriodsServiceCallerButtons(Interface):
    """Holiday periods service caller buttons interface"""

    download = SubmitButton(name='download', title=_("Download holidays"))
    close = CloseButton(name='close', title=_("Close"))


@ajax_form_config(name='download-periods.html',
                  context=IHolidayPeriodTable, layer=IPyAMSLayer,
                  permission=MANAGE_TOOL_PERMISSION)
class HolidayPeriodsServiceCallerForm(AdminModalAddForm):
    """Holiday periods service caller form"""
    
    fields = Fields(IHolidayPeriodsServiceCallerFields)
    buttons = Buttons(IHolidayPeriodsServiceCallerButtons)
    
    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        scholar_year = self.widgets.get('scholar_year')
        if scholar_year is not None:
            scholar_year.prompt = True
            scholar_year.prompt_message = _("Please select a scholar year...")
        populations = self.widgets.get('populations')
        if populations is not None:
            populations.no_value_message = _("(all selected populations)")
    
    @handler(buttons['download'])
    def handle_download(self, action):
        self.handle_add(self, action)
        
    def create_and_add(self, data):
        data = data.get(self, data)
        service = create_object(IHolidayPeriodsGetterService)
        if service is not None:
            return service.get_periods(scholar_year=data.get('scholar_year'),
                                       populations=data.get('populations'))
        return 0
    
        
@adapter_config(name='download',
                required=(IHolidayPeriodTable, IAdminLayer, HolidayPeriodsServiceCallerForm),
                provides=IAJAXFormRenderer)
class HolidayPeriodsServiceCallerFormRenderer(ContextRequestViewAdapter):
    """Holiday periods service caller form renderer"""
    
    def render(self, changes):
        if not changes:
            return None
        translate = self.request.localizer.translate
        return {
            'status': 'reload',
            'smallbox': {
                'status': 'success',
                'message': translate(_("{} holidays periods have been downloaded!")).format(changes)
            }
        }
