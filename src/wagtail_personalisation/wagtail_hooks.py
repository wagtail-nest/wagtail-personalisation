from __future__ import absolute_import, unicode_literals

import logging

from django.conf.urls import include, url
from django.core.urlresolvers import reverse
from django.template.defaultfilters import pluralize
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.site_summary import SummaryItem, PagesSummaryItem
from wagtail.wagtailadmin.widgets import Button, ButtonWithDropdownFromHook
from wagtail.wagtailcore import hooks
from wagtail.wagtailcore.models import Page

from wagtail_personalisation import admin_urls, models, utils
from wagtail_personalisation.adapters import get_segment_adapter

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
def serve_variant(page, request, serve_args, serve_kwargs):
    """Apply a segment to a visitor before serving the page.

    :param page: The page being served
    :type page: wagtail.wagtailcore.models.Page
    :param request: The http request
    :type request: django.http.HttpRequest
    :returns: A variant if one is available for the visitor's segment,
              otherwise the original page
    :rtype: wagtail.wagtailcore.models.Page

    """
    user_segments = []
    if not isinstance(page, models.PersonalisablePageMixin):
        return

    adapter = get_segment_adapter(request)
    user_segments = adapter.get_segments()

    if user_segments:
        metadata = page.personalisation_metadata

        # TODO: This is never more then one page? (fix query count)
        metadata = metadata.metadata_for_segments(user_segments)
        if metadata:
            variant = metadata.first().variant.specific
            return variant.serve(request, *serve_args, **serve_kwargs)


@hooks.register('construct_explorer_page_queryset')
def dont_show_variant(parent_page, pages, request):
    return utils.exclude_variants(pages)


@hooks.register('register_page_listing_buttons')
def page_listing_variant_buttons(page, page_perms, is_parent=False):
    """Adds page listing buttons to personalisable pages. Shows variants for
    the page (if any) and a 'Create a new variant' button.

    """
    if not isinstance(page, models.PersonalisablePageMixin):
        return

    metadata = page.personalisation_metadata
    if metadata.is_canonical:
        yield ButtonWithDropdownFromHook(
            _('Variants'),
            hook_name='register_page_listing_variant_buttons',
            page=page,
            page_perms=page_perms,
            is_parent=is_parent,
            attrs={'target': '_blank', 'title': _('Create or edit a variant')},
            priority=100)


@hooks.register('register_page_listing_variant_buttons')
def page_listing_more_buttons(page, page_perms, is_parent=False):
    """Adds a 'more' button to personalisable pages allowing users to quickly
    create a new variant for the selected segment.

    """
    if not isinstance(page, models.PersonalisablePageMixin):
        return

    metadata = page.personalisation_metadata

    for vm in metadata.variants_metadata:
        yield Button('%s variant' % (vm.segment.name),
                     reverse('wagtailadmin_pages:edit', args=[vm.variant_id]),
                     attrs={"title": _('Edit this variant')},
                     classes=("icon", "icon-fa-pencil"),
                     priority=0)

    for segment in metadata.get_unused_segments():
        yield Button('%s variant' % (segment.name),
                     reverse('segment:copy_page', args=[page.pk, segment.pk]),
                     attrs={"title": _('Create this variant')},
                     classes=("icon", "icon-fa-plus"),
                     priority=100)

    yield Button(_('Create a new segment'),
                 reverse('wagtail_personalisation_segment_modeladmin_create'),
                 attrs={"title": _('Create a new segment')},
                 classes=("icon", "icon-fa-snowflake-o"),
                 priority=200)


class CorrectedPagesSummaryPanel(PagesSummaryItem):
    def get_context(self):
        context = super(CorrectedPagesSummaryPanel, self).get_context()

        pages = utils.exclude_variants(Page.objects.all().specific())

        context['total_pages'] = len(pages) - 1
        return context


@hooks.register('construct_homepage_summary_items')
def add_corrected_pages_summary_panel(request, items):
    """Replaces the Pages summary panel to hide variants."""
    for index, item in enumerate(items):
        if item.__class__ is PagesSummaryItem:
            items[index] = CorrectedPagesSummaryPanel(request)


class SegmentSummaryPanel(SummaryItem):
    """The segment summary panel showing the total amount of segments on the
    site and allowing quick access to the Segment dashboard.

    """
    order = 2000

    def render(self):
        segment_count = models.Segment.objects.count()
        target_url = reverse('wagtail_personalisation_segment_modeladmin_index')
        title = _("Segments")
        return mark_safe("""
            <li class="icon icon-fa-snowflake-o">
                <a href="{}"><span>{}</span>{}</a>
            </li>""".format(target_url, segment_count, title))


class PersonalisedPagesSummaryPanel(PagesSummaryItem):
    order = 2100

    def render(self):
        page_count = models.PersonalisablePageMetadata.objects.filter(
            segment__isnull=True).count()
        title = _("Personalised Page")
        return mark_safe("""
            <li class="icon icon-fa-file-o">
                <span>{}</span>{}{}
            </li>""".format(page_count, title, pluralize(page_count)))


class VariantPagesSummaryPanel(PagesSummaryItem):
    order = 2200

    def render(self):
        page_count = models.PersonalisablePageMetadata.objects.filter(
            segment__isnull=False).count()
        title = _("Variant")
        return mark_safe("""
                <li class="icon icon-fa-files-o">
                    <span>{}</span>{}{}
                </li>""".format(page_count, title, pluralize(page_count)))


@hooks.register('construct_homepage_summary_items')
def add_personalisation_summary_panels(request, items):
    """Adds a summary panel to the Wagtail dashboard showing the total amount
    of segments on the site and allowing quick access to the Segment
    dashboard.

    """
    items.append(SegmentSummaryPanel(request))
    items.append(PersonalisedPagesSummaryPanel(request))
    items.append(VariantPagesSummaryPanel(request))
