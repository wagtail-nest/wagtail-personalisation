import pytest
from django.http import Http404
from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail.models import Page
else:
    from wagtail.core.models import Page

from tests.factories.page import ContentPageFactory
from tests.factories.segment import SegmentFactory
from wagtail_personalisation import adapters, wagtail_hooks


@pytest.mark.django_db
def test_serve_variant_no_variant(site, rf):
    page = site.root_page
    request = rf.get("/")
    args = tuple()
    kwargs = {}

    result = wagtail_hooks.serve_variant(page, request, args, kwargs)
    assert result is None


@pytest.mark.django_db
def test_variant_accessed_directly_returns_404(segmented_page, rf):
    request = rf.get("/")
    args = tuple()
    kwargs = {}
    with pytest.raises(Http404):
        wagtail_hooks.serve_variant(segmented_page, request, args, kwargs)


@pytest.mark.django_db
def test_serve_variant_with_variant_no_segment(site, rf, segmented_page):
    request = rf.get("/")
    args = tuple()
    kwargs = {}

    page = segmented_page.personalisation_metadata.canonical_page
    result = wagtail_hooks.serve_variant(page, request, args, kwargs)
    assert result is None


@pytest.mark.django_db
def test_serve_variant_with_variant_segmented(site, rf, segmented_page):
    request = rf.get("/")
    args = tuple()
    kwargs = {}

    page = segmented_page.personalisation_metadata.canonical_page
    segment = segmented_page.personalisation_metadata.segment

    adapter = adapters.get_segment_adapter(request)
    adapter.set_segments([segment])

    result = wagtail_hooks.serve_variant(page, request, args, kwargs)
    assert result.status_code == 200


@pytest.mark.django_db
def test_page_listing_variant_buttons(site, rf, segmented_page):
    page = segmented_page.personalisation_metadata.canonical_page

    SegmentFactory(name="something")
    result = wagtail_hooks.page_listing_variant_buttons(page, [])
    items = list(result)
    assert len(items) == 1


@pytest.mark.django_db
def test_page_listing_more_buttons(site, rf, segmented_page):
    page = segmented_page.personalisation_metadata.canonical_page

    SegmentFactory(name="something")
    result = wagtail_hooks.page_listing_more_buttons(page, [])
    items = list(result)
    assert len(items) == 3


@pytest.mark.django_db
def test_custom_delete_page_view_does_not_trigger_for_variants(rf, segmented_page):
    assert (wagtail_hooks.delete_related_variants(rf.get("/"), segmented_page)) is None


@pytest.mark.django_db
def test_custom_delete_page_view_triggers_for_canonical_pages(rf, segmented_page):
    assert (
        wagtail_hooks.delete_related_variants(
            rf.get("/"), segmented_page.personalisation_metadata.canonical_page
        )
    ) is not None


@pytest.mark.django_db
def test_custom_delete_page_view_deletes_variants(rf, segmented_page, user):
    post_request = rf.post("/")
    user.is_superuser = True
    rf.user = user
    canonical_page = segmented_page.personalisation_metadata.canonical_page
    canonical_page_variant = canonical_page.personalisation_metadata
    assert canonical_page_variant

    variants = Page.objects.filter(
        pk__in=(
            canonical_page.personalisation_metadata.variants_metadata.values_list(
                "variant_id", flat=True
            )
        )
    )
    variants_metadata = canonical_page.personalisation_metadata.variants_metadata
    # Make sure there are variants that exist in the database.
    assert len(variants.all())
    assert len(variants_metadata.all())
    wagtail_hooks.delete_related_variants(
        post_request, segmented_page.personalisation_metadata.canonical_page
    )
    with pytest.raises(canonical_page.DoesNotExist):
        canonical_page.refresh_from_db()
    with pytest.raises(canonical_page_variant.DoesNotExist):
        canonical_page_variant.refresh_from_db()
    # Make sure all the variant pages have been deleted.
    assert not len(variants.all())
    assert not len(variants_metadata.all())


@pytest.mark.django_db
def test_custom_delete_page_view_deletes_variants_of_child_pages(
    rf, segmented_page, user
):
    """
    Regression test for deleting pages that have children with variants
    """
    post_request = rf.post("/")
    user.is_superuser = True
    rf.user = user
    canonical_page = segmented_page.personalisation_metadata.canonical_page
    # Create a child with a variant
    child_page = ContentPageFactory(parent=canonical_page, slug="personalised-child")
    child_page.personalisation_metadata.copy_for_segment(
        segmented_page.personalisation_metadata.segment
    )
    # A ProtectedError would be raised if the bug persists
    wagtail_hooks.delete_related_variants(post_request, canonical_page)
