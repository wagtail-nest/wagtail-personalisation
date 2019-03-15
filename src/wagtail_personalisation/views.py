import csv

from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import (
    HttpResponse, HttpResponseForbidden, HttpResponseRedirect)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import DeleteView, IndexView
from wagtail.core.models import Page

from wagtail_personalisation.models import Segment
from wagtail_personalisation.utils import can_delete_pages


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


class SegmentModelDeleteView(DeleteView):
    def get_affected_page_objects(self):
        return Page.objects.filter(pk__in=(
            self.instance.get_used_pages().values_list('variant_id', flat=True)
        ))

    def get_template_names(self):
        return [
            'modeladmin/wagtail_personalisation/segment/delete.html',
            'modeladmin/delete.html',
        ]

    def delete_instance(self):
        page_variants = self.get_affected_page_objects()
        if not can_delete_pages(page_variants, self.request.user):
            raise PermissionDenied(
                'User has no permission to delete variant page objects.'
            )
        # Deleting page objects triggers deletion of the personalisation
        # metadata too because of models.CASCADE.
        with transaction.atomic():
            for variant in page_variants.iterator():
                # Delete each one separately so signals are called.
                variant.delete()
            super().delete_instance()

    def post(self, request, *args, **kwargs):
        if not can_delete_pages(self.get_affected_page_objects(),
                                self.request.user):
            context = self.get_context_data(
                cannot_delete_page_variants_error=True,
            )
            return self.render_to_response(context)
        return super().post(request, *args, **kwargs)


@modeladmin_register
class SegmentModelAdmin(ModelAdmin):
    """The model admin for the Segments administration interface."""
    model = Segment
    index_view_class = SegmentModelIndexView
    dashboard_view_class = SegmentModelDashboardView
    delete_view_class = SegmentModelDeleteView
    menu_icon = 'fa-snowflake-o'
    add_to_settings_menu = False
    list_display = ('name', 'persistent', 'match_any', 'status',
                    'page_count', 'variant_count', 'statistics')
    index_view_extra_js = ['js/commons.js', 'js/index.js']
    index_view_extra_css = ['css/index.css']
    form_view_extra_js = ['js/commons.js', 'js/form.js',
                          'js/segment_form_control.js',
                          'wagtailadmin/js/page-chooser-modal.js',
                          'wagtailadmin/js/page-chooser.js']
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


# CSV download views
def segment_user_data(request, segment_id):
    if request.user.has_perm('wagtailadmin.access_admin'):
        segment = get_object_or_404(Segment, pk=segment_id)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = \
            'attachment;filename=segment-%s-users.csv' % str(segment_id)

        headers = ['Username']
        for rule in segment.get_rules():
            if rule.static:
                headers.append(rule.get_column_header())

        writer = csv.writer(response)
        writer.writerow(headers)

        for user in segment.static_users.all():
            row = [user.username]
            for rule in segment.get_rules():
                if rule.static:
                    row.append(rule.get_user_info_string(user))
            writer.writerow(row)

        return response

    return HttpResponseForbidden()
