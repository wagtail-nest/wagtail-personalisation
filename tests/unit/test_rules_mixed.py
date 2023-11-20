from __future__ import absolute_import, unicode_literals

import datetime

import pytest
from freezegun import freeze_time

from tests.factories.rule import ReferralRuleFactory, TimeRuleFactory
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
def test_no_segments(client, site):
    response = client.get("/")
    assert response.status_code == 200
    assert client.session["segments"] == []


@pytest.mark.django_db
def test_referral_segment(client, site):
    referral_segment = SegmentFactory(name="Referral")
    ReferralRuleFactory(regex_string="test.test", segment=referral_segment)

    response = client.get("/", **{"HTTP_REFERER": "test.test"})
    assert response.status_code == 200

    assert client.session["segments"][0]["encoded_name"] == "referral"


@pytest.mark.django_db
@freeze_time("10:00:00")
def test_time_and_referral_segment(client, site):
    segment = SegmentFactory(name="Both")
    TimeRuleFactory(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment,
    )
    ReferralRuleFactory(regex_string="test.test", segment=segment)

    response = client.get("/", **{"HTTP_REFERER": "test.test"})
    assert response.status_code == 200

    assert client.session["segments"][0]["encoded_name"] == "both"


@pytest.mark.django_db
@freeze_time("7:00:00")
def test_no_time_but_referral_segment(client, site):
    segment = SegmentFactory(name="Not both")
    TimeRuleFactory(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment,
    )
    ReferralRuleFactory(regex_string="test.test", segment=segment)

    response = client.get("/", **{"HTTP_REFERER": "test.test"})
    assert response.status_code == 200

    assert len(client.session["segments"]) == 0


@pytest.mark.django_db
@freeze_time("9:00:00")
def test_time_but_no_referral_segment(client, site):
    segment = SegmentFactory(name="Not both")
    TimeRuleFactory(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment,
    )
    ReferralRuleFactory(regex_string="test.test", segment=segment)

    response = client.get("/")
    assert response.status_code == 200

    assert len(client.session["segments"]) == 0
