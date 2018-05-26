from __future__ import absolute_import, unicode_literals

import datetime

import pytest

from tests.factories.segment import SegmentFactory
from tests.factories.page import ContentPageFactory
from wagtail_personalisation.rules import TimeRule
from tests.site.pages import models


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
def test_content_page_model():
    page = ContentPageFactory()
    qs = models.ContentPage.objects.all()
    assert page in qs
