import pytest

from tests.factories.rule import DeviceRuleFactory
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
def test_device_rule_create():
    segment = SegmentFactory(name="DeviceSegment")
    device_rule = DeviceRuleFactory(mobile=True, segment=segment)

    assert device_rule.mobile is True
    assert device_rule.tablet is False
    assert device_rule.desktop is False


@pytest.mark.django_db
def test_request_device_segment(client, site):
    device_only_segment = SegmentFactory(name="Device only")
    DeviceRuleFactory(tablet=True, segment=device_only_segment)

    client.get(
        "/",
        **{"HTTP_USER_AGENT": "Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X)"}
    )

    assert client.session["segments"][0]["encoded_name"] == "device-only"


@pytest.mark.django_db
def test_request_device_segment_no_match(client, site):
    no_device_segment = SegmentFactory(name="No device")
    DeviceRuleFactory(mobile=True, segment=no_device_segment)

    client.get(
        "/",
        **{"HTTP_USER_AGENT": "Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X)"}
    )

    assert not client.session["segments"]
