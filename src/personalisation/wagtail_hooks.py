from django.conf import settings
from django.conf.urls import include, url
from django.core.urlresolvers import reverse

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.wagtailcore import hooks

from personalisation import admin_urls
from personalisation.models import Segment


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^personalisation/', include(admin_urls, app_name='personalisation', namespace='personalisation')),
    ]


"""
The base model for the Segments administration interface
"""
class SegmentModelAdmin(ModelAdmin):
    model = Segment
    menu_icon = 'group'
    add_to_settings_menu = False
    list_display = ('status', 'name')
    inspect_view_enabled = True
    index_view_extra_css = ['personalisation/segment/index.css']
    form_view_extra_css = ['personalisation/segment/form.css']

modeladmin_register(SegmentModelAdmin)


"""
Update the users visit count before each page visit
"""
@hooks.register('before_serve_page')
def set_visit_count(page, request, serve_args, serve_kwargs):
    if request.session.get('visit_count'):
        request.session['visit_count'] = request.session.get('visit_count') + 1
    else:
        request.session['visit_count'] = 1