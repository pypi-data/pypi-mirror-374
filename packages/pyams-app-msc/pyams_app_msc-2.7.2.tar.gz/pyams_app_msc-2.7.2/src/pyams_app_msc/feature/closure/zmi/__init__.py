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

from pyams_app_msc.feature.closure import IClosurePeriod, IClosurePeriodContainer, IClosurePeriodContainerTarget
from pyams_app_msc.feature.closure.zmi.interfaces import IClosurePeriodContainerTable
from pyams_app_msc.interfaces import MANAGE_THEATER_PERMISSION, VIEW_THEATER_PERMISSION
from pyams_app_msc.shared.theater import IMovieTheater
from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.view import IModalEditForm
from pyams_skin.viewlet.actions import ContextAddAction
from pyams_utils.adapter import adapter_config
from pyams_utils.traversing import get_parent
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm, SimpleAddFormRenderer, SimpleEditFormRenderer
from pyams_zmi.interfaces import IAdminLayer, IObjectHint, IObjectLabel
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IToolbarViewletManager
from pyams_zmi.table import TableElementEditor
from pyams_zmi.utils import get_object_label

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


@viewlet_config(name='add-closure-period.action',
                context=IClosurePeriodContainerTarget, layer=IAdminLayer,
                view=IClosurePeriodContainerTable, manager=IToolbarViewletManager, weight=20,
                permission=MANAGE_THEATER_PERMISSION)
class ClosurePeriodAddAction(ContextAddAction):
    """Closure period add action"""
    
    label = _("Add closure period")
    href = 'add-closure-period.html'


@ajax_form_config(name='add-closure-period.html',
                  context=IClosurePeriodContainerTarget, layer=IPyAMSLayer,
                  permission=MANAGE_THEATER_PERMISSION)
class ClosurePeriodAddForm(AdminModalAddForm):
    """Closure period add form"""
    
    subtitle = _("New closure period")
    legend =_("new closure period properties")
    
    content_factory = IClosurePeriod
    fields = Fields(IClosurePeriod).omit('__parent__', '__name__', 'active')
    
    def add(self, obj):
        IClosurePeriodContainer(self.context).append(obj)


@adapter_config(required=(IClosurePeriodContainerTarget, IAdminLayer, ClosurePeriodAddForm),
                provides=IFormTitle)
def closure_period_add_form_title(context, request, form):
    """Closure period add form title"""
    return '<span class="tiny">{}</span>'.format(
        get_object_label(context, request, form))


@adapter_config(required=(IClosurePeriodContainerTarget, IAdminLayer, ClosurePeriodAddForm),
                provides=IAJAXFormRenderer)
class ClosurePeriodAddFormRenderer(SimpleAddFormRenderer):
    """Closure period add form renderer"""

    table_factory = IClosurePeriodContainerTable


@adapter_config(required=(IClosurePeriod, IAdminLayer, Interface),
                provides=IObjectLabel)
def closure_period_label(context, request, view):
    """Closure period label"""
    return context.label


@adapter_config(required=(IClosurePeriod, IAdminLayer, Interface),
                provides=IObjectHint)
def closure_period_hint(context, request, view):
    """Closure period hint"""
    return request.localizer.translate(_("Closure period"))


@adapter_config(required=(IClosurePeriod, IAdminLayer, IClosurePeriodContainerTable),
                provides=ITableElementEditor)
class ClosurePeriodEditor(TableElementEditor):
    """Closure period editor"""


@ajax_form_config(name='properties.html',
                  context=IClosurePeriod, layer=IPyAMSLayer,
                  permission=VIEW_THEATER_PERMISSION)
class ClosurePeriodPropertiesEditForm(AdminModalEditForm):
    """Closure period properties edit form"""

    legend = _("Closure period properties")

    fields = Fields(IClosurePeriod).omit('__parent__', '__name__', 'active')


@adapter_config(required=(IClosurePeriod, IAdminLayer, IModalEditForm),
                provides=IFormTitle)
def closure_period_edit_form_title(context, request, form):
    translate = request.localizer.translate
    theater = get_parent(context, IMovieTheater)
    return '<span class="tiny">{}</span><br />{}'.format(
        get_object_label(theater, request, form),
        translate(_("Closure period: {}")).format(get_object_label(context, request, form)))


@adapter_config(required=(IClosurePeriod, IAdminLayer, ClosurePeriodPropertiesEditForm),
                provides=IAJAXFormRenderer)
class ClosurePeriodPropertiesEditFormRenderer(SimpleEditFormRenderer):
    """Closure period properties edit form renderer"""

    parent_interface = IClosurePeriodContainerTarget
    table_factory = IClosurePeriodContainerTable
