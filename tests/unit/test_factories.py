from __future__ import absolute_import, unicode_literals

import datetime

import pytest

from tests.factories.rule import QueryRuleFactory, ReferralRuleFactory
from tests.factories.segment import SegmentFactory
from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import TimeRule

# Factory tests


@pytest.mark.django_db
def test_segment_create():
    factoried_segment = SegmentFactory()
    segment = Segment(name="TestSegment", status="enabled")
    TimeRule(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment,
    )

    assert factoried_segment.name == segment.name
    assert factoried_segment.status == segment.status


@pytest.mark.django_db
def test_referral_rule_create():
    segment = SegmentFactory(name="Referral")
    referral_rule = ReferralRuleFactory(regex_string="test.test", segment=segment)

    assert referral_rule.regex_string == "test.test"


@pytest.mark.django_db
def test_query_rule_create():
    segment = SegmentFactory(name="Query")
    query_rule = QueryRuleFactory(parameter="query", value="value", segment=segment)

    assert query_rule.parameter == "query"
    assert query_rule.value == "value"
