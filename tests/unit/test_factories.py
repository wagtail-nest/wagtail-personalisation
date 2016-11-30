import datetime

import pytest

from personalisation.models import Segment, TimeRule
from tests.factories.segment import SegmentFactory, TimeRuleFactory, ReferralRuleFactory

"""Factory tests"""
@pytest.mark.django_db
def test_create_segment_factory():
    factoried_segment = SegmentFactory()
    segment = Segment(name='TestSegment', status='enabled')
    time_rule = TimeRule(start_time=datetime.time(8,0,0), end_time=datetime.time(23,0,0), segment=segment)

    assert factoried_segment.name == segment.name
    assert factoried_segment.status == segment.status
    assert factoried_segment.time_rule.start_time == time_rule.start_time

"""TimeRuleFactory tests"""
@pytest.mark.django_db
def test_create_segment_with_time_rule():
    segment = SegmentFactory()

    assert segment.time_rule.start_time == datetime.time(8,0,0)

@pytest.mark.django_db
def test_create_segment_with_new_time_rule():
    segment = SegmentFactory()
    segment.time_rule = TimeRuleFactory(start_time=datetime.time(9,0,0), segment=segment)

    assert segment.time_rule.start_time == datetime.time(9,0,0)

"""ReferralRuleFactory tests"""
@pytest.mark.django_db
def test_create_segment_with_referral_rule():
    segment = SegmentFactory()

    assert segment.referral_rule.regex_string == "test.test"

@pytest.mark.django_db
def test_create_segment_with_new_referral_rule():
    segment = SegmentFactory()

    segment.referral_rule = ReferralRuleFactory(regex_string="test.notest", segment=segment)

    assert segment.referral_rule.regex_string == "test.notest"
