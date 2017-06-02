from __future__ import absolute_import, unicode_literals

import datetime

import pytest

from tests.factories.segment import SegmentFactory
from wagtail_personalisation.rules import TimeRule


@pytest.mark.django_db
def test_segment_create():
    segment = SegmentFactory()
    TimeRule(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment)


@pytest.mark.django_db
def test_metadata_page_has_variations(segmented_page):
    assert not segmented_page.personalisable_metadata.is_canonical
    assert not segmented_page.personalisable_metadata.has_variations

    canonical = segmented_page.personalisable_metadata.canonical_page
    assert canonical.personalisable_metadata.is_canonical
    assert canonical.personalisable_metadata.has_variations
