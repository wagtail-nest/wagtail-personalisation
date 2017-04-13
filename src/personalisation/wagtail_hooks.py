from __future__ import absolute_import, unicode_literals

import logging

from django.conf.urls import include, url
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import IndexView
from wagtail.wagtailadmin.widgets import Button, ButtonWithDropdownFromHook
from wagtail.wagtailcore import hooks

from personalisation import admin_urls
from personalisation.app_settings import segments_adapter
from personalisation.models import PersonalisablePage, Segment
from personalisation.utils import impersonate_other_page

logger = logging.getLogger(__name__)


@hooks.register('register_admin_urls')
def register_admin_urls():
    """Adds the administration urls for the personalisation apps."""
    return [
        url(r'^personalisation/', include(
            admin_urls,
            app_name='personalisation',
            namespace='personalisation')),
    ]


class SegmentModelIndexView(IndexView):
    pass


class SegmentModelAdmin(ModelAdmin):
    """The base model for the Segments administration interface."""
    model = Segment
    index_view_class = SegmentModelIndexView
    menu_icon = 'group'
    add_to_settings_menu = False
    list_display = ('status', 'name', 'create_date', 'edit_date')
    index_view_extra_css = ['personalisation/segment/index.css']
    form_view_extra_css = ['personalisation/segment/form.css']

modeladmin_register(SegmentModelAdmin)


@hooks.register('before_serve_page')
def set_visit_count(page, request, serve_args, serve_kwargs):
    if 'visit_count' not in request.session:
        request.session['visit_count'] = []

    # Update the page visit count
    def create_new_counter(page, request):
        """Create a new counter dict and place it in session storage."""
        countdict = {
            "slug": page.slug,
            "id": page.pk,
            "path": request.path,
            "count": 1,
        }
        request.session['visit_count'].append(countdict)

    if len(request.session['visit_count']) > 0:
        for index, counter in enumerate(request.session['visit_count']):
            if counter['id'] == page.pk:
                # Counter already exists. Increase the count value by 1.
                newcount = counter['count'] + 1
                request.session['visit_count'][index]['count'] = newcount
                request.session.modified = True
            else:
                # Counter doesn't exist.
                # Create a new counter with count value 1.
                create_new_counter(page, request)
    else:
        # No counters exist. Create a new counter with count value 1.
        create_new_counter(page, request)


@hooks.register('before_serve_page')
def segment_user(page, request, serve_args, serve_kwargs):
    segments_adapter.setup(request)
    segments_adapter.refresh()


@hooks.register('before_serve_page')
def serve_variation(page, request, serve_args, serve_kwargs):
    user_segments = []

    for segment in segments_adapter.get_all_segments():
        try:
            user_segment = Segment.objects.get(pk=segment['id'],
                                               status='enabled')
        except Segment.DoesNotExist:
            user_segment = None
        if user_segment:
            user_segments.append(user_segment)

    if len(user_segments) > 0:
        variations = _check_for_variations(user_segments, page)

        if variations:
            variation = variations[0]

            impersonate_other_page(variation, page)

            return variation.serve(request, *serve_args, **serve_kwargs)


def _check_for_variations(segments, page):
    for segment in segments:
        page_class = page.__class__
        if not any(item == PersonalisablePage for item in page_class.__bases__):
            page_class = PersonalisablePage

        variation = page_class.objects.filter(
            canonical_page=page, segment=segment)

        if variation:
            return variation

    return None


@hooks.register('register_page_listing_buttons')
def page_listing_variant_buttons(page, page_perms, is_parent=False):
    personalisable_page = PersonalisablePage.objects.filter(pk=page.pk)
    segments = Segment.objects.all()

    if personalisable_page and len(segments) > 0 and not (any(item.segment for item in personalisable_page)):
        yield ButtonWithDropdownFromHook(
            _('Variants'),
            hook_name='register_page_listing_variant_buttons',
            page=page,
            page_perms=page_perms,
            is_parent=is_parent,
            attrs={'target': '_blank', 'title': _('Create a new variant')}, priority=100)


@hooks.register('register_page_listing_variant_buttons')
def page_listing_more_buttons(page, page_perms, is_parent=False):
    segments = Segment.objects.all()
    available_segments = [item for item in segments if not PersonalisablePage.objects.filter(segment=item, pk=page.pk)]

    for segment in available_segments:
        yield Button(segment.name,
                     reverse('segment:copy_page', args=[page.id, segment.id]),
                     attrs={"title": _('Create this variant')})


class SegmentSummaryPanel(object):
    order = 500

    def render(self):
        segment_count = Segment.objects.count()
        target_url = reverse('personalisation_segment_modeladmin_index')
        title = _("Segments")
        return mark_safe("""
            <li class="icon icon-group">
                <a href="{}"><span>{}</span>{}</a>
            </li>""".format(target_url, segment_count, title))


@hooks.register('construct_homepage_summary_items')
def add_segment_summary_panel(request, summary_items):
    return summary_items.append(SegmentSummaryPanel())
