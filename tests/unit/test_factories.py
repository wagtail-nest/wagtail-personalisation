from __future__ import absolute_import, unicode_literals

import datetime

import pytest

from personalisation.models import Segment
from personalisation.rules import TimeRule
from tests.factories.segment import (
    ReferralRuleFactory, SegmentFactory, TimeRuleFactory, DayRuleFactory, DeviceRuleFactory)

"""Factory tests"""
@pytest.mark.django_db
def test_create_segment_factory():
    factoried_segment = SegmentFactory()
    segment = Segment(name='TestSegment', status='enabled')
    time_rule = TimeRule(start_time=datetime.time(8,0,0), end_time=datetime.time(23,0,0), segment=segment)

    assert factoried_segment.name == segment.name
    assert factoried_segment.status == segment.status


"""TimeRuleFactory tests"""
@pytest.mark.django_db
def test_create_segment_with_time_rule():
    segment = SegmentFactory(name='TimeSegment')
    time_rule = TimeRuleFactory(start_time=datetime.time(8, 0, 0), end_time=datetime.time(23, 0, 0), segment=segment)

    assert time_rule.start_time == datetime.time(8,0,0)


"""TimeRuleFactory tests"""
@pytest.mark.django_db
def test_create_segment_with_day_rule():
    segment = SegmentFactory(name='DaySegment')
    day_rule = DayRuleFactory(mon=True, thu=True, segment=segment)

    assert day_rule.mon is True
    assert day_rule.thu is True
    assert day_rule.sun is False


"""DeviceRuleFactory tests"""
@pytest.mark.django_db
def test_create_segment_with_device_rule():
    segment = SegmentFactory(name='DeviceSegment')
    device_rule = DeviceRuleFactory(mobile=True, segment=segment)

    assert device_rule.mobile is True
    assert device_rule.tablet is False
    assert device_rule.desktop is False


"""ReferralRuleFactory tests"""
@pytest.mark.django_db
def test_create_segment_with_referral_rule():
    segment = SegmentFactory(name='Referral')
    referral_rule = ReferralRuleFactory(regex_string='test.test', segment=segment)

    assert referral_rule.regex_string == 'test.test'


@pytest.mark.django_db
def test_create_segment_with_new_referral_rule():
    segment = SegmentFactory()

    segment.referral_rule = ReferralRuleFactory(regex_string='test.notest', segment=segment)

    assert segment.referral_rule.regex_string == 'test.notest'
