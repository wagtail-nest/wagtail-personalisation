from __future__ import absolute_import, unicode_literals

import datetime

import pytest

from tests.factories.segment import SegmentFactory
from wagtail_personalisation.rules import TimeRule
from wagtail_personalisation.models import Segment


@pytest.mark.django_db
def test_segment_create():
    segment = SegmentFactory()
    TimeRule(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment)


@pytest.mark.django_db
def test_metadata_page_has_variants(segmented_page):
    assert not segmented_page.personalisation_metadata.is_canonical
    assert not segmented_page.personalisation_metadata.has_variants

    canonical = segmented_page.personalisation_metadata.canonical_page
    assert canonical.personalisation_metadata.is_canonical
    assert canonical.personalisation_metadata.has_variants


@pytest.mark.django_db
def test_segment_edit_view(site, client, django_user_model):
    test_segment = Segment()
    new_panel = test_segment.panels[1].children[0].bind_to_model(Segment)
    assert new_panel.related.name == "wagtail_personalisation_timerules"
