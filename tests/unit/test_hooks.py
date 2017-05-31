import pytest

from wagtail_personalisation import wagtail_hooks as hooks
from wagtail_personalisation.models import Segment


@pytest.mark.django_db
def test_check_for_variations(segmented_page):
    segments = Segment.objects.all()
    page = segmented_page.canonical_page

    variations = hooks._check_for_variations(segments, page)
    assert variations
