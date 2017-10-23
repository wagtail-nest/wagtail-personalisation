from __future__ import absolute_import, unicode_literals

import datetime

import pytest

from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from tests.factories.segment import SegmentFactory
from wagtail_personalisation.forms import SegmentAdminForm
from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import TimeRule, VisitCountRule


@pytest.mark.django_db
def test_session_added_to_static_segment_at_creation(rf, site, client):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory(type=Segment.TYPE_STATIC)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)
    segment.save()

    # We need to trigger the post init
    segment = Segment.objects.get(id=segment.id)

    assert session.session_key in segment.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_mixed_static_dynamic_session_doesnt_generate_at_creation(rf, site, client):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory(type=Segment.TYPE_STATIC)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)
    TimeRule.objects.create(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
        segment=segment,
    )
    segment.save()

    # We need to trigger the post init
    segment = Segment.objects.get(id=segment.id)

    assert not segment.sessions.all()


@pytest.mark.django_db
def test_session_not_added_to_static_segment_after_creation(rf, site, client):
    segment = SegmentFactory(type=Segment.TYPE_STATIC)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)
    segment.save()

    session = client.session
    session.save()
    client.get(site.root_page.url)

    assert not segment.sessions.all()


@pytest.mark.django_db
def test_session_added_to_static_segment_after_creation(rf, site, client):
    segment = SegmentFactory(type=Segment.TYPE_STATIC, count=1)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)
    segment.save()

    session = client.session
    session.save()
    client.get(site.root_page.url)

    assert session.session_key in segment.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_session_not_added_to_static_segment_after_full(rf, site, client):
    segment = SegmentFactory(type=Segment.TYPE_STATIC, count=1)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)
    segment.save()

    session = client.session
    session.save()
    client.get(site.root_page.url)

    second_session = client.session
    second_session.create()
    client.get(site.root_page.url)

    assert session.session_key != second_session.session_key
    assert segment.sessions.count() == 1
    assert session.session_key in segment.sessions.values_list('session_key', flat=True)
    assert second_session.session_key not in segment.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_sessions_not_added_to_static_segment_if_rule_not_static(client, site):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory(type=Segment.TYPE_STATIC)
    TimeRule.objects.create(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
        segment=segment,
    )
    segment.save()

    assert not segment.sessions.all()


@pytest.mark.django_db
def test_does_not_calculate_the_segment_again(rf, site, client, mocker):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory(type=Segment.TYPE_STATIC, count=2)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)
    segment.save()

    mock_test_rule = mocker.patch('wagtail_personalisation.adapters.SessionSegmentsAdapter._test_rules')
    client.get(site.root_page.url)
    assert mock_test_rule.call_count == 0


def form_with_data(segment, rule):
    model_fields = ['type', 'status', 'count', 'name']

    class TestSegmentAdminForm(SegmentAdminForm):
        class Meta:
            model = Segment
            fields = model_fields

    data = model_to_dict(segment, model_fields)
    for formset in TestSegmentAdminForm().formsets.values():
        rule_data = {}
        if isinstance(rule, formset.model):
            rule_data = model_to_dict(rule)
            for key, value in rule_data.items():
                data['{}-0-{}'.format(formset.prefix, key)] = value
        data['{}-INITIAL_FORMS'.format(formset.prefix)] = 0
        data['{}-TOTAL_FORMS'.format(formset.prefix)] = 1 if rule_data else 0
    return TestSegmentAdminForm(data)



@pytest.mark.django_db
def test_non_static_rules_have_a_count():
    segment = SegmentFactory(type=Segment.TYPE_STATIC, count=0)
    rule = TimeRule.objects.create(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
        segment=segment,
    )
    form = form_with_data(segment, rule)
    assert not form.is_valid()


@pytest.mark.django_db
def test_static_segment_with_static_rules_needs_no_count(site):
    segment = SegmentFactory(type=Segment.TYPE_STATIC, count=0)
    rule = VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)
    form = form_with_data(segment, rule)
    assert form.is_valid()


@pytest.mark.django_db
def test_dynamic_segment_with_non_static_rules_have_a_count():
    segment = SegmentFactory(type=Segment.TYPE_DYNAMIC, count=0)
    rule = TimeRule.objects.create(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
        segment=segment,
    )
    form = form_with_data(segment, rule)
    assert form.is_valid(), form.errors
