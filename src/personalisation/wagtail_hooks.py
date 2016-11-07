from django.conf import settings
from django.conf.urls import include, url
from django.core.urlresolvers import reverse
from wagtail.wagtailadmin import widgets
from wagtail.wagtailadmin.menu import MenuItem

from personalisation import admin_urls
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.wagtailcore import hooks

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
    search_fields = ('name')

modeladmin_register(SegmentModelAdmin)
