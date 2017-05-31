import pytest

from wagtail_personalisation.models import Segment


@pytest.mark.django_db
def test_variants(segmented_page):
    segments = Segment.objects.all()
    page = segmented_page.canonical_page

    variations = page.variants_for_segments(segments)
    assert variations
