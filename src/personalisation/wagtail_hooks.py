from django.conf.urls import include, url
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import IndexView
from wagtail.wagtailcore import hooks

from personalisation import admin_urls
from personalisation.models import Segment


@hooks.register('register_admin_urls')
def register_admin_urls():
    """Adds the administration urls for the personalisation apps."""
    return [
        url(r'^personalisation/', include(
            admin_urls,
            app_name='personalisation',
            namespace='personalisation')),
    ]


class SegmentModelAdmin(ModelAdmin):
    """The base model for the Segments administration interface."""
    model = Segment
    menu_icon = 'group'
    add_to_settings_menu = False
    list_display = ('status', 'name', 'create_date', 'edit_date')
    index_view_extra_css = ['personalisation/segment/index.css']
    form_view_extra_css = ['personalisation/segment/form.css']
    inspect_view_enabled = True

modeladmin_register(SegmentModelAdmin)


@hooks.register('before_serve_page')
def set_visit_count(page, request, serve_args, serve_kwargs):
    """Update the users visit count before each page visit."""
    for seg in request.session['segments']:
        segment = Segment.objects.get(pk=seg['id'])
        segment.visit_count = segment.visit_count + 1
        segment.save()

    if 'visit_count' not in request.session:
        request.session['visit_count'] = 1
    else:
        request.session['visit_count'] = request.session.get('visit_count') + 1
