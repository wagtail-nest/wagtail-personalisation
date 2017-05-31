from __future__ import absolute_import, unicode_literals

import logging

from django.conf.urls import include, url
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.site_summary import SummaryItem
from wagtail.wagtailadmin.widgets import Button, ButtonWithDropdownFromHook
from wagtail.wagtailcore import hooks

from wagtail_personalisation import admin_urls
from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import PersonalisablePage, Segment
from wagtail_personalisation.utils import impersonate_other_page

logger = logging.getLogger(__name__)


@hooks.register('register_admin_urls')
def register_admin_urls():
    """Adds the administration urls for the personalisation apps."""
    return [
        url(r'^personalisation/', include(
            admin_urls,
            app_name='wagtail_personalisation',
            namespace='wagtail_personalisation')),
    ]


@hooks.register('before_serve_page')
def set_visit_count(page, request, serve_args, serve_kwargs):
    """Tests the provided rules to see if the request still belongs
    to a segment.

    :param page: The page being served
    :type page: wagtail.wagtailcore.models.Page
    :param request: The http request
    :type request: django.http.HttpRequest

    """
    adapter = get_segment_adapter(request)
    adapter.add_page_visit(page)


@hooks.register('before_serve_page')
def segment_user(page, request, serve_args, serve_kwargs):
    """Apply a segment to a visitor before serving the page.

    :param page: The page being served
    :type page: wagtail.wagtailcore.models.Page
    :param request: The http request
    :type request: django.http.HttpRequest

    """
    adapter = get_segment_adapter(request)
    adapter.refresh()


@hooks.register('before_serve_page')
def serve_variation(page, request, serve_args, serve_kwargs):
    """Apply a segment to a visitor before serving the page.

    :param page: The page being served
    :type page: wagtail.wagtailcore.models.Page
    :param request: The http request
    :type request: django.http.HttpRequest
    :returns: A variation if one is available for the visitor's segment,
              otherwise the original page
    :rtype: wagtail.wagtailcore.models.Page

    """
    user_segments = []
    adapter = get_segment_adapter(request)

    for segment in adapter.get_all_segments():
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
    """Check whether there are variations available for the provided segments
    on the page being served.

    :param segments: The segments applicable to the request.
    :type segments: list of wagtail_personalisation.models.Segment
    :param page: The page being served
    :type page: wagtail_personalisation.models.PersonalisablePage or
                wagtail.wagtailcore.models.Page
    :returns: A variant of the requested page matching the segments or None
    :rtype: wagtail_personalisation.models.PersonalisablePage or None

    """
    for segment in segments:
        page_class = page.__class__
        if any(item == PersonalisablePage for item in page_class.__bases__):

            variation = page_class.objects.filter(
                canonical_page=page, segment=segment)

            if variation:
                return variation

    return None


@hooks.register('register_page_listing_buttons')
def page_listing_variant_buttons(page, page_perms, is_parent=False):
    """Adds page listing buttons to personalisable pages. Shows variants for
    the page (if any) and a 'Create a new variant' button.

    """
    personalisable_page = PersonalisablePage.objects.filter(pk=page.pk)
    segments = Segment.objects.all()

    if personalisable_page and len(segments) > 0 and not (
            any(item.segment for item in personalisable_page)):
        yield ButtonWithDropdownFromHook(
            _('Variants'),
            hook_name='register_page_listing_variant_buttons',
            page=page,
            page_perms=page_perms,
            is_parent=is_parent,
            attrs={'target': '_blank', 'title': _('Create a new variant')},
            priority=100)


@hooks.register('register_page_listing_variant_buttons')
def page_listing_more_buttons(page, page_perms, is_parent=False):
    """Adds a 'more' button to personalisable pages allowing users to quickly
    create a new variant for the selected segment.

    """
    segments = Segment.objects.all()
    available_segments = [
        item for item in segments
        if not PersonalisablePage.objects.filter(segment=item, pk=page.pk)
    ]

    for segment in available_segments:
        yield Button(segment.name,
                     reverse('segment:copy_page', args=[page.id, segment.id]),
                     attrs={"title": _('Create this variant')})


class SegmentSummaryPanel(SummaryItem):
    """The segment summary panel showing the total amount of segments on the
    site and allowing quick access to the Segment dashboard.

    """
    order = 500

    def render(self):
        segment_count = Segment.objects.count()
        target_url = reverse('wagtail_personalisation_segment_modeladmin_index')
        title = _("Segments")
        return mark_safe("""
            <li class="icon icon-group">
                <a href="{}"><span>{}</span>{}</a>
            </li>""".format(target_url, segment_count, title))


@hooks.register('construct_homepage_summary_items')
def add_segment_summary_panel(request, items):
    """Adds a summary panel to the Wagtail dashboard showing the total amount
    of segments on the site and allowing quick access to the Segment dashboard.

    """
    return items.append(SegmentSummaryPanel(request))
