from __future__ import absolute_import, unicode_literals

import datetime

import pytest

from tests.factories.page import HomePageFactory
from tests.factories.rule import (
    DayRuleFactory, DeviceRuleFactory, ReferralRuleFactory, TimeRuleFactory)
from tests.factories.segment import SegmentFactory
from tests.factories.site import SiteFactory
from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import TimeRule


# Factory tests

@pytest.mark.django_db
def test_create_segment_factory():
    factoried_segment = SegmentFactory()
    segment = Segment(name='TestSegment', status='enabled')
    TimeRule(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment)

    assert factoried_segment.name == segment.name
    assert factoried_segment.status == segment.status


# TimeRuleFactory tests

@pytest.mark.django_db
def test_create_segment_with_time_rule():
    segment = SegmentFactory(name='TimeSegment')
    time_rule = TimeRuleFactory(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment)

    assert time_rule.start_time == datetime.time(8, 0, 0)


# TimeRuleFactory tests

@pytest.mark.django_db
def test_create_segment_with_day_rule():
    segment = SegmentFactory(name='DaySegment')
    day_rule = DayRuleFactory(mon=True, thu=True, segment=segment)

    assert day_rule.mon is True
    assert day_rule.thu is True
    assert day_rule.sun is False


# DeviceRuleFactory tests

@pytest.mark.django_db
def test_create_segment_with_device_rule():
    segment = SegmentFactory(name='DeviceSegment')
    device_rule = DeviceRuleFactory(mobile=True, segment=segment)

    assert device_rule.mobile is True
    assert device_rule.tablet is False
    assert device_rule.desktop is False


# ReferralRuleFactory tests

@pytest.mark.django_db
def test_create_segment_with_referral_rule():
    segment = SegmentFactory(name='Referral')
    referral_rule = ReferralRuleFactory(
        regex_string='test.test',
        segment=segment)

    assert referral_rule.regex_string == 'test.test'


@pytest.mark.django_db
def test_create_segment_with_new_referral_rule():
    segment = SegmentFactory()

    segment.referral_rule = ReferralRuleFactory(
        regex_string='test.notest',
        segment=segment)

    assert segment.referral_rule.regex_string == 'test.notest'


@pytest.mark.django_db
def test_site_factory():
    site = SiteFactory()
    assert site


@pytest.mark.django_db
def test_page_factory():
    site = SiteFactory()
    assert site.root_page
    page = HomePageFactory(parent=site.root_page)
    assert page.get_parent() == site.root_page
