from __future__ import absolute_import, unicode_literals

import datetime

from django.forms.models import model_to_dict
from django.contrib.sessions.backends.db import SessionStore
import pytest
from wagtail_personalisation.forms import SegmentAdminForm
from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import TimeRule, VisitCountRule

from tests.factories.segment import SegmentFactory


def form_with_data(segment, *rules):
    model_fields = ['type', 'status', 'count', 'name', 'match_any']

    class TestSegmentAdminForm(SegmentAdminForm):
        class Meta:
            model = Segment
            fields = model_fields

    data = model_to_dict(segment, model_fields)
    for formset in TestSegmentAdminForm().formsets.values():
        rule_data = {}
        count = 0
        for rule in rules:
            if isinstance(rule, formset.model):
                rule_data = model_to_dict(rule)
                for key, value in rule_data.items():
                    data['{}-{}-{}'.format(formset.prefix, count, key)] = value
                count += 1
        data['{}-INITIAL_FORMS'.format(formset.prefix)] = 0
        data['{}-TOTAL_FORMS'.format(formset.prefix)] = count
    return TestSegmentAdminForm(data)


@pytest.mark.django_db
def test_session_added_to_static_segment_at_creation(site, client):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    assert instance.frozen
    assert session.session_key in instance.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_match_any_correct_populates(site, client):
    session = client.session
    client.get(site.root_page.url)

    client.cookies.clear()
    second_session = client.session
    other_page = site.root_page.get_last_child()
    client.get(other_page.url)

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, match_any=True)
    rule_1 = VisitCountRule(counted_page=site.root_page)
    rule_2 = VisitCountRule(counted_page=other_page)
    form = form_with_data(segment, rule_1, rule_2)
    instance = form.save()

    assert instance.frozen
    assert session.session_key != second_session.session_key
    assert session.session_key in instance.sessions.values_list('session_key', flat=True)
    assert second_session.session_key in instance.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_mixed_static_dynamic_session_doesnt_generate_at_creation(site, client):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    static_rule = VisitCountRule(counted_page=site.root_page)
    non_static_rule = TimeRule(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
    )
    form = form_with_data(segment, static_rule, non_static_rule)
    instance = form.save()

    assert instance.frozen
    assert not instance.sessions.all()


@pytest.mark.django_db
def test_session_not_added_to_static_segment_after_creation(site, client):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=0)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    session = client.session
    session.save()
    client.get(site.root_page.url)

    assert instance.frozen
    assert not instance.sessions.all()


@pytest.mark.django_db
def test_session_added_to_static_segment_after_creation(site, client):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    session = client.session
    session.save()
    client.get(site.root_page.url)

    assert instance.frozen
    assert session.session_key in instance.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_session_not_added_to_static_segment_after_full(site, client):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    assert instance.frozen
    assert instance.sessions.count() == 0

    session = client.session
    client.get(site.root_page.url)

    assert instance.sessions.count() == 1

    client.cookies.clear()
    second_session = client.session
    client.get(site.root_page.url)

    assert session.session_key != second_session.session_key
    assert instance.sessions.count() == 1
    assert session.session_key in instance.sessions.values_list('session_key', flat=True)
    assert second_session.session_key not in instance.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_sessions_not_added_to_static_segment_if_rule_not_static(client, site):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    rule = TimeRule(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
        segment=segment,
    )
    form = form_with_data(segment, rule)
    instance = form.save()

    assert instance.frozen
    assert not instance.sessions.all()


@pytest.mark.django_db
def test_does_not_calculate_the_segment_again(site, client, mocker):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=2)
    rule = VisitCountRule(counted_page=site.root_page, segment=segment)
    form = form_with_data(segment, rule)
    instance = form.save()
    assert instance.frozen
    assert session.session_key in instance.sessions.values_list('session_key', flat=True)

    mock_test_rule = mocker.patch('wagtail_personalisation.adapters.SessionSegmentsAdapter._test_rules')
    client.get(site.root_page.url)
    assert mock_test_rule.call_count == 0


@pytest.mark.django_db
def test_non_static_rules_have_a_count():
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=0)
    rule = TimeRule(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
        segment=segment,
    )
    form = form_with_data(segment, rule)
    assert not form.is_valid()


@pytest.mark.django_db
def test_static_segment_with_static_rules_needs_no_count(site):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=0)
    rule = VisitCountRule(counted_page=site.root_page, segment=segment)
    form = form_with_data(segment, rule)
    assert form.is_valid()


@pytest.mark.django_db
def test_dynamic_segment_with_non_static_rules_have_a_count():
    segment = SegmentFactory.build(type=Segment.TYPE_DYNAMIC, count=0)
    rule = TimeRule(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
    )
    form = form_with_data(segment, rule)
    assert form.is_valid(), form.errors
