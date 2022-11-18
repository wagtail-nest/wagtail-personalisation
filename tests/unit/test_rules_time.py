import datetime

import pytest
from freezegun import freeze_time

from tests.factories.rule import TimeRuleFactory
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
def test_time_rule_create():
    segment = SegmentFactory(name="TimeSegment")
    time_rule = TimeRuleFactory(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment,
    )

    assert time_rule.start_time == datetime.time(8, 0, 0)


@pytest.mark.django_db
@freeze_time("10:00:00")
def test_requesttime_segment(client, site):
    time_only_segment = SegmentFactory(name="Time only")
    TimeRuleFactory(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=time_only_segment,
    )

    response = client.get("/")
    assert response.status_code == 200

    assert client.session["segments"][0]["encoded_name"] == "time-only"
