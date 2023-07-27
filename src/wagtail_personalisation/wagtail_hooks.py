import logging

from django.db import transaction
from django.db.models import F
from django.http import Http404
from django.shortcuts import redirect, render
from django.template.defaultfilters import pluralize
from django.urls import include, re_path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin import messages
from wagtail.admin.site_summary import PagesSummaryItem, SummaryItem
from wagtail.admin.views.pages.utils import get_valid_next_url_from_request
from wagtail.admin.widgets import Button, ButtonWithDropdownFromHook
from wagtail.models import Page

from wagtail_personalisation import admin_urls, models, utils
from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import PersonalisablePageMetadata

logger = logging.getLogger(__name__)


@hooks.register("register_admin_urls")
def register_admin_urls():
    """Adds the administration urls for the personalisation apps."""
    return [
        re_path(
            r"^personalisation/",
            include(admin_urls, namespace="wagtail_personalisation"),
        )
    ]


@hooks.register("before_serve_page")
def set_visit_count(page, request, serve_args, serve_kwargs):
    """Tests the provided rules to see if the request still belongs
    to a segment.

    :param page: The page being served
    :type page: wagtail.models.Page
    :param request: The http request
    :type request: django.http.HttpRequest

    """
    adapter = get_segment_adapter(request)
    adapter.add_page_visit(page)


@hooks.register("before_serve_page")
def segment_user(page, request, serve_args, serve_kwargs):
    """Apply a segment to a visitor before serving the page.

    :param page: The page being served
    :type page: wagtail.models.Page
    :param request: The http request
    :type request: django.http.HttpRequest

    """
    adapter = get_segment_adapter(request)
    adapter.refresh()

    forced_segment = request.GET.get("segment", None)
    if request.user.is_superuser and forced_segment is not None:
        segment = models.Segment.objects.filter(pk=forced_segment).first()
        if segment:
            adapter.set_segments([segment])


class UserbarSegmentedLinkItem:
    def __init__(self, segment):
        self.segment = segment

    def render(self, request):
        return f"""<div class="wagtail-userbar__item">
            <a href="{request.path}?segment={self.segment.pk}"
                class="wagtail-action">
                    Show as segment: {self.segment.name}</a></div>"""


@hooks.register("construct_wagtail_userbar")
def add_segment_link_items(request, items):
    for item in models.Segment.objects.enabled():
        items.append(UserbarSegmentedLinkItem(item))
    return items


@hooks.register("before_serve_page")
def serve_variant(page, request, serve_args, serve_kwargs):
    """Apply a segment to a visitor before serving the page.

    :param page: The page being served
    :type page: wagtail.models.Page
    :param request: The http request
    :type request: django.http.HttpRequest
    :returns: A variant if one is available for the visitor's segment,
              otherwise the original page
    :rtype: wagtail.models.Page

    """
    user_segments = []
    if not isinstance(page, models.PersonalisablePageMixin):
        return

    adapter = get_segment_adapter(request)
    user_segments = adapter.get_segments()

    metadata = page.personalisation_metadata

    # If page is not canonical, don't serve it.
    if not metadata.is_canonical:
        raise Http404

    if user_segments:
        # TODO: This is never more then one page? (fix query count)
        metadata = metadata.metadata_for_segments(user_segments)
        if metadata:
            variant = metadata.first().variant.specific
            return variant.serve(request, *serve_args, **serve_kwargs)


@hooks.register("construct_explorer_page_queryset")
def dont_show_variant(parent_page, pages, request):
    return utils.exclude_variants(pages)


@hooks.register("register_page_listing_buttons")
def page_listing_variant_buttons(page, page_perms, *args, **is_parent):
    """Adds page listing buttons to personalisable pages. Shows variants for
    the page (if any) and a 'Create a new variant' button.

    """
    if not isinstance(page, models.PersonalisablePageMixin):
        return

    metadata = page.personalisation_metadata

    if metadata.is_canonical:
        yield ButtonWithDropdownFromHook(
            _("Variants"),
            hook_name="register_page_listing_variant_buttons",
            page=page,
            page_perms=page_perms,
            attrs={"target": "_blank", "title": _("Create or edit a variant")},
            priority=100,
        )


@hooks.register("register_page_listing_variant_buttons")
def page_listing_more_buttons(page, page_perms, is_parent=False, *args):
    """Adds a 'more' button to personalisable pages allowing users to quickly
    create a new variant for the selected segment.

    """
    if not isinstance(page, models.PersonalisablePageMixin):
        return

    metadata = page.personalisation_metadata

    for vm in metadata.variants_metadata:
        yield Button(
            "%s variant" % (vm.segment.name),
            reverse("wagtailadmin_pages:edit", args=[vm.variant_id]),
            attrs={"title": _("Edit this variant")},
            classes=("icon", "icon-fa-pencil"),
            priority=0,
        )

    for segment in metadata.get_unused_segments():
        yield Button(
            "%s variant" % (segment.name),
            reverse("segment:copy_page", args=[page.pk, segment.pk]),
            attrs={"title": _("Create this variant")},
            classes=("icon", "icon-fa-plus"),
            priority=100,
        )

    yield Button(
        _("Create a new segment"),
        reverse("wagtail_personalisation_segment_modeladmin_create"),
        attrs={"title": _("Create a new segment")},
        classes=("icon", "icon-fa-snowflake-o"),
        priority=200,
    )


class CorrectedPagesSummaryItem(PagesSummaryItem):
    def get_total_pages(self, context):
        # Perform the same check as Wagtail to get the correct count.
        # Only correct the count when a root page is available to the user.
        # The `PagesSummaryItem` will return a page count of 0 otherwise.
        # https://github.com/wagtail/wagtail/blob/5c9ff23e229acabad406c42c4e13cbaea32e6c15/wagtail/admin/site_summary.py#L38
        root_page = context.get("root_page", None)
        if root_page:
            pages = utils.exclude_variants(
                Page.objects.descendant_of(root_page, inclusive=True)
            )
            page_count = pages.count()

            if root_page.is_root():
                page_count -= 1

            return page_count

    def get_context_data(self, parent_context):
        context = super().get_context_data(parent_context)
        context["total_pages"] = self.get_total_pages(context)
        return context


@hooks.register("construct_homepage_summary_items")
def add_corrected_pages_summary_panel(request, items):
    """Replaces the Pages summary panel to hide variants."""
    for index, item in enumerate(items):
        if item.__class__ is PagesSummaryItem:
            items[index] = CorrectedPagesSummaryItem(request)


class SegmentSummaryPanel(SummaryItem):
    """The segment summary panel showing the total amount of segments on the
    site and allowing quick access to the Segment dashboard.

    """

    order = 2000

    def render_html(self, parent_context):
        segment_count = models.Segment.objects.count()
        target_url = reverse("wagtail_personalisation_segment_modeladmin_index")
        title = _("Segments")
        return mark_safe(
            """
            <li>
                <svg class="icon icon-tag icon" aria-hidden="true"><use href="#icon-tag"></use></svg>
                <a href="{}"><span>{}</span>{}</a>
            </li>""".format(
                target_url, segment_count, title
            )
        )


class PersonalisedPagesSummaryPanel(PagesSummaryItem):
    order = 2100

    def render_html(self, parent_context):
        page_count = models.PersonalisablePageMetadata.objects.filter(
            segment__isnull=True
        ).count()
        title = _("Personalised Page")
        return mark_safe(
            """
            <li>
                <svg class="icon icon-doc-empty icon" aria-hidden="true"><use href="#icon-doc-empty"></use></svg>
                <a><span>{}</span>{}{}</a>
            </li>""".format(
                page_count, title, pluralize(page_count)
            )
        )


class VariantPagesSummaryPanel(PagesSummaryItem):
    order = 2200

    def render_html(self, parent_context):
        page_count = models.PersonalisablePageMetadata.objects.filter(
            segment__isnull=False
        ).count()
        title = _("Variant")
        return mark_safe(
            """
                <li>
                    <svg class="icon icon-doc-empty icon" aria-hidden="true">\n
                    <use href="#icon-doc-empty"></use></svg>
                    <a><span>{}</span>{}{}</a>
                </li>""".format(
                page_count, title, pluralize(page_count)
            )
        )


@hooks.register("construct_homepage_summary_items")
def add_personalisation_summary_panels(request, items):
    """Adds a summary panel to the Wagtail dashboard showing the total amount
    of segments on the site and allowing quick access to the Segment
    dashboard.

    """
    items.append(SegmentSummaryPanel(request))
    items.append(PersonalisedPagesSummaryPanel(request))
    items.append(VariantPagesSummaryPanel(request))


@hooks.register("before_delete_page")
def delete_related_variants(request, page):
    if (
        not isinstance(page, models.PersonalisablePageMixin)
        or not page.personalisation_metadata.is_canonical
    ):
        return
    # Get a list of related personalisation metadata for all the related
    # variants.
    variants_metadata = page.personalisation_metadata.variants_metadata.select_related(
        "variant"
    )
    next_url = get_valid_next_url_from_request(request)

    if request.method == "POST":
        parent_id = page.get_parent().id
        with transaction.atomic():
            # To ensure variants are deleted for all descendants, start with
            # the deepest ones, and explicitly delete variants and metadata
            # for all of them, including the page itself. Otherwise protected
            # foreign key constraints are violated. Only consider canonical
            # pages.
            for metadata in PersonalisablePageMetadata.objects.filter(
                canonical_page__in=page.get_descendants(inclusive=True),
                variant=F("canonical_page"),
            ).order_by("-canonical_page__depth"):
                for variant_metadata in metadata.variants_metadata.select_related(
                    "variant"
                ):
                    # Call delete() on objects to trigger any signals or hooks.
                    variant_metadata.variant.delete()
                metadata.delete()
                metadata.canonical_page.delete()

        msg = _("Page '{0}' and its variants deleted.")
        messages.success(request, msg.format(page.get_admin_display_title()))

        for fn in hooks.get_hooks("after_delete_page"):
            result = fn(request, page)
            if hasattr(result, "status_code"):
                return result

        if next_url:
            return redirect(next_url)
        return redirect("wagtailadmin_explore", parent_id)

    return render(
        request,
        "wagtailadmin/pages/wagtail_personalisation/confirm_delete.html",
        {
            "page": page,
            "descendant_count": page.get_descendant_count(),
            "next": next_url,
            "variants": Page.objects.filter(
                pk__in=variants_metadata.values_list("variant_id")
            ),
        },
    )
