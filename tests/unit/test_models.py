import datetime

import pytest
from django.db.models import ProtectedError

from tests.factories.page import ContentPageFactory
from tests.factories.segment import SegmentFactory
from tests.site.pages import models
from wagtail_personalisation.models import PersonalisablePageMetadata, Segment
from wagtail_personalisation.rules import AbstractBaseRule, TimeRule


@pytest.mark.django_db
def test_segment_create():
    segment = SegmentFactory()
    TimeRule(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment,
    )


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


@pytest.mark.django_db
def test_variant_can_be_deleted_without_error(segmented_page):
    segmented_page.delete()
    # Make sure the metadata gets deleted because of models.CASCADE.
    with pytest.raises(PersonalisablePageMetadata.DoesNotExist):
        segmented_page._personalisable_page_metadata.refresh_from_db()


@pytest.mark.django_db
def test_canonical_page_deletion_is_protected(segmented_page):
    # When deleting canonical page without deleting variants, it should return
    # an error. All variants should be deleted beforehand.
    with pytest.raises(ProtectedError):
        segmented_page.personalisation_metadata.canonical_page.delete()


@pytest.mark.django_db
def test_page_protection_when_deleting_segment(segmented_page):
    segment = segmented_page.personalisation_metadata.segment
    assert len(segment.get_used_pages())
    with pytest.raises(ProtectedError):
        segment.delete()


@pytest.mark.django_db
def test_sitemap_generation_for_canonical_pages_is_enabled(segmented_page):
    canonical = segmented_page.personalisation_metadata.canonical_page
    assert canonical.personalisation_metadata.is_canonical
    assert canonical.get_sitemap_urls()


@pytest.mark.django_db
def test_sitemap_generation_for_variants_is_disabled(segmented_page):
    assert not segmented_page.personalisation_metadata.is_canonical
    assert not segmented_page.get_sitemap_urls()


@pytest.mark.django_db
def test_segment_edit_view(site, client, django_user_model):
    test_segment = SegmentFactory()
    new_panel = test_segment.panels[1].children[0].bind_to_model(Segment)
    assert new_panel.related.name == "wagtail_personalisation_timerules"


@pytest.mark.django_db
def test_segment_panels_include_all_rules_by_default():
    """Test that all rules are included when WAGTAIL_PERSONALISATION_RULES is not set."""
    segment = SegmentFactory()
    # Get the rules MultiFieldPanel (second panel)
    rules_panel = segment.panels[1]

    # Count the number of rule panels
    rule_panel_count = len(rules_panel.children)

    # Count all AbstractBaseRule subclasses
    all_rules_count = len(AbstractBaseRule.__subclasses__())

    assert rule_panel_count == all_rules_count


@pytest.mark.django_db
def test_segment_panels_filtered_by_setting(settings):
    """Test that only specified rules are included when WAGTAIL_PERSONALISATION_RULES is set."""
    # Set the filter to only include TimeRule and DayRule
    settings.WAGTAIL_PERSONALISATION_RULES = [
        'wagtail_personalisation.TimeRule',
        'wagtail_personalisation.DayRule',
    ]

    # Create a new segment instance to trigger __init__ with the new setting
    segment = Segment()

    # Get the rules MultiFieldPanel (second panel)
    rules_panel = segment.panels[1]

    # Count the number of rule panels
    rule_panel_count = len(rules_panel.children)

    # Should only have 2 rules
    assert rule_panel_count == 2

    # Verify the rule names
    rule_names = [child.relation_name for child in rules_panel.children]
    assert 'wagtail_personalisation_timerule_related' in rule_names
    assert 'wagtail_personalisation_dayrule_related' in rule_names
