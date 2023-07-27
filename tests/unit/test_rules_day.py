from __future__ import absolute_import, unicode_literals

import pytest
from freezegun import freeze_time

from tests.factories.rule import DayRuleFactory
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
def test_day_rule_create():
    segment = SegmentFactory(name="DaySegment")
    day_rule = DayRuleFactory(mon=True, thu=True, segment=segment)

    assert day_rule.mon is True
    assert day_rule.thu is True
    assert day_rule.sun is False


@pytest.mark.django_db
@freeze_time("2017-01-01")
def test_request_day_segment(client, site):
    day_only_segment = SegmentFactory(name="Day only")
    DayRuleFactory(sun=True, segment=day_only_segment)

    client.get("/")

    assert client.session["segments"][0]["encoded_name"] == "day-only"
