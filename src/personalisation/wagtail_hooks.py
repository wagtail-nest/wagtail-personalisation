from django.conf import settings
from django.conf.urls import include, url
from django.core.urlresolvers import reverse
<<<<<<< HEAD
from wagtail.wagtailadmin import widgets
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailadmin.modal_workflow import render_modal_workflow

from personalisation import admin_urls
=======
>>>>>>> master
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.wagtailadmin import widgets
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from personalisation import admin_urls
from personalisation.models import Segment


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^personalisation/', include(admin_urls, app_name='personalisation', namespace='personalisation')),
    ]


class SegmentModelAdmin(ModelAdmin):
    model = Segment
    menu_icon = 'group'
    add_to_settings_menu = False
    list_display = ('name')
    index_view_extra_css = ['personalisation/segment/index.css']
    form_view_extra_css = ['personalisation/segment/form.css']

modeladmin_register(SegmentModelAdmin)
