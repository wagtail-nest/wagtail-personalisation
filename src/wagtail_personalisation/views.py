from __future__ import absolute_import, unicode_literals

from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import IndexView
from wagtail.wagtailcore.models import Page

from wagtail_personalisation.models import Segment


class SegmentModelIndexView(IndexView):
    """Placeholder for additional list functionality."""
    pass


class SegmentModelDashboardView(IndexView):
    """Additional dashboard functionality."""
    def media(self):
        return forms.Media(
            css={'all': ['css/dashboard.css']},
            js=['js/commons.js', 'js/dashboard.js']
        )

    def get_template_names(self):
        return [
            'modeladmin/wagtail_personalisation/segment/dashboard.html',
            'modeladmin/index.html'
        ]


@modeladmin_register
class SegmentModelAdmin(ModelAdmin):
    """The model admin for the Segments administration interface."""
    model = Segment
    index_view_class = SegmentModelIndexView
    dashboard_view_class = SegmentModelDashboardView
    menu_icon = 'fa-snowflake-o'
    add_to_settings_menu = False
    list_display = ('name', 'persistent', 'match_any', 'status',
                    'page_count', 'variant_count', 'statistics')
    index_view_extra_js = ['js/commons.js', 'js/index.js']
    index_view_extra_css = ['css/index.css']
    form_view_extra_js = ['js/commons.js', 'js/form.js']
    form_view_extra_css = ['css/form.css']

    def index_view(self, request):
        kwargs = {'model_admin': self}
        view_class = self.dashboard_view_class

        request.session.setdefault('segment_view', 'dashboard')
        if request.session['segment_view'] != 'dashboard':
            view_class = self.index_view_class

        return view_class.as_view(**kwargs)(request)

    def page_count(self, obj):
        return len(obj.get_used_pages())

    def variant_count(self, obj):
        return len(obj.get_created_variants())

    def statistics(self, obj):
        return _("{visits} visits in {days} days").format(
            visits=obj.visit_count, days=obj.get_active_days())


def toggle_segment_view(request):
    """Toggle between the list view and dashboard view.

    :param request: The http request
    :type request: django.http.HttpRequest
    :returns: A redirect to the original page
    :rtype: django.http.HttpResponseRedirect

    """
    if request.user.has_perm('wagtailadmin.access_admin'):
        if request.session['segment_view'] == 'dashboard':
            request.session['segment_view'] = 'list'

        elif request.session['segment_view'] != 'dashboard':
            request.session['segment_view'] = 'dashboard'

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponseForbidden()


def toggle(request, segment_id):
    """Toggle the status of the selected segment.

    :param request: The http request
    :type request: django.http.HttpRequest
    :param segment_id: The primary key of the segment
    :type segment_id: int
    :returns: A redirect to the original page
    :rtype: django.http.HttpResponseRedirect

    """
    if request.user.has_perm('wagtailadmin.access_admin'):
        segment = get_object_or_404(Segment, pk=segment_id)

        segment.toggle()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponseForbidden()


def copy_page_view(request, page_id, segment_id):
    """Copy page with selected segment. If the page for the selected segment
    already exists the user will be redirected to that particular page.

    :param request: The http request
    :type request: django.http.HttpRequest
    :param page_id: The primary key of the page
    :type segment_id: int
    :param segment_id: The primary key of the segment
    :type segment_id: int
    :returns: A redirect to the new page
    :rtype: django.http.HttpResponseRedirect

    """
    if request.user.has_perm('wagtailadmin.access_admin'):
        segment = get_object_or_404(Segment, pk=segment_id)
        page = get_object_or_404(Page, pk=page_id).specific

        metadata = page.personalisation_metadata
        variant_metadata = metadata.metadata_for_segments([segment])
        if variant_metadata.exists():
            variant = variant_metadata.first()
        else:
            variant = metadata.copy_for_segment(segment)
        edit_url = reverse('wagtailadmin_pages:edit', args=[variant.id])

        return HttpResponseRedirect(edit_url)

    return HttpResponseForbidden()
