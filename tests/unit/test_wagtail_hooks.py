import pytest

from wagtail_personalisation import adapters, wagtail_hooks


@pytest.mark.django_db
def test_serve_variation_no_variant(site, rf):
    page = site.root_page
    request = rf.get('/')
    args = tuple()
    kwargs = {}

    result = wagtail_hooks.serve_variation(page, request, args, kwargs)
    assert result is None


@pytest.mark.django_db
def test_serve_variation_with_variant_no_segment(site, rf, segmented_page):
    request = rf.get('/')
    args = tuple()
    kwargs = {}

    page = segmented_page.personalisation_metadata.canonical_page
    result = wagtail_hooks.serve_variation(page, request, args, kwargs)
    assert result is None


@pytest.mark.django_db
def test_serve_variation_with_variant_segmented(site, rf, segmented_page):
    request = rf.get('/')
    args = tuple()
    kwargs = {}

    page = segmented_page.personalisation_metadata.canonical_page
    segment = segmented_page.personalisation_metadata.segment

    adapter = adapters.get_segment_adapter(request)
    adapter.set_segments([segment])

    result = wagtail_hooks.serve_variation(page, request, args, kwargs)
    assert result.status_code == 200
