from importlib.util import find_spec
from unittest.mock import MagicMock, call, patch

import pytest

from tests.factories.rule import OriginCountryRuleFactory
from tests.factories.segment import SegmentFactory
from wagtail_personalisation.rules import get_geoip_module

skip_if_geoip2_installed = pytest.mark.skipif(
    find_spec("geoip2"), reason="requires GeoIP2 to be not installed"
)

skip_if_geoip2_not_installed = pytest.mark.skipif(
    not find_spec("geoip2"), reason="requires GeoIP2 to be installed."
)


@pytest.mark.django_db
def test_get_cloudflare_country_with_header(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/", HTTP_CF_IPCOUNTRY="PL")
    assert rule.get_cloudflare_country(request) == "pl"


@pytest.mark.django_db
def test_get_cloudflare_country_with_no_header(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/")
    assert "HTTP_CF_IPCOUNTRY" not in request.META
    assert rule.get_cloudflare_country(request) is None


@pytest.mark.django_db
def test_get_cloudfront_country_with_header(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/", HTTP_CLOUDFRONT_VIEWER_COUNTRY="BY")
    assert rule.get_cloudfront_country(request) == "by"


@pytest.mark.django_db
def test_get_cloudfront_country_with_no_header(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/")
    assert "HTTP_CLOUDFRONT_VIEWER_COUNTRY" not in request.META
    assert rule.get_cloudfront_country(request) is None


@pytest.mark.django_db
def test_get_geoip_country_with_remote_addr(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/", REMOTE_ADDR="173.254.89.34")
    geoip_mock = MagicMock()
    with patch(
        "wagtail_personalisation.rules.get_geoip_module", return_value=geoip_mock
    ) as geoip_import_mock:
        rule.get_geoip_country(request)
    geoip_import_mock.assert_called_once()
    geoip_mock.assert_called_once()
    assert geoip_mock.mock_calls[1] == call().country_code("173.254.89.34")


@pytest.mark.django_db
def test_get_country_calls_all_methods(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/")

    @patch.object(rule, "get_geoip_country", return_value="")
    @patch.object(rule, "get_cloudflare_country", return_value="")
    @patch.object(rule, "get_cloudfront_country", return_value="")
    def test_mock(cloudfront_mock, cloudflare_mock, geoip_mock):
        country = rule.get_country(request)
        cloudflare_mock.assert_called_once_with(request)
        cloudfront_mock.assert_called_once_with(request)
        geoip_mock.assert_called_once_with(request)
        assert country is None

    test_mock()


@pytest.mark.django_db
def test_get_country_does_not_use_all_detection_methods_unnecessarily(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/")

    @patch.object(rule, "get_geoip_country", return_value="")
    @patch.object(rule, "get_cloudflare_country", return_value="t1")
    @patch.object(rule, "get_cloudfront_country", return_value="")
    def test_mock(cloudfront_mock, cloudflare_mock, geoip_mock):
        country = rule.get_country(request)
        cloudflare_mock.assert_called_once_with(request)
        cloudfront_mock.assert_not_called()
        geoip_mock.assert_not_called()
        assert country == "t1"

    test_mock()


@pytest.mark.django_db
def test_test_user_calls_get_country(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/")
    with patch.object(rule, "get_country") as get_country_mock:
        rule.test_user(request)
    get_country_mock.assert_called_once_with(request)


@pytest.mark.django_db
def test_test_user_returns_true_if_cloudflare_country_match(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/", HTTP_CF_IPCOUNTRY="GB")
    assert rule.test_user(request) is True


@pytest.mark.django_db
def test_test_user_returns_false_if_cloudflare_country_doesnt_match(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/", HTTP_CF_IPCOUNTRY="NL")
    assert not rule.test_user(request)


@pytest.mark.django_db
def test_test_user_returns_false_if_cloudfront_country_doesnt_match(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="GB")
    request = rf.get("/", HTTP_CLOUDFRONT_VIEWER_COUNTRY="NL")
    assert rule.test_user(request) is False


@pytest.mark.django_db
def test_test_user_returns_true_if_cloudfront_country_matches(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="se")
    request = rf.get("/", HTTP_CLOUDFRONT_VIEWER_COUNTRY="SE")
    assert rule.test_user(request) is True


@skip_if_geoip2_not_installed
@pytest.mark.django_db
def test_test_user_geoip_module_matches(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="se")
    request = rf.get("/", REMOTE_ADDR="123.120.0.2")
    GeoIP2Mock = MagicMock()
    GeoIP2Mock().configure_mock(**{"country_code.return_value": "SE"})
    GeoIP2Mock.reset_mock()
    with patch(
        "wagtail_personalisation.rules.get_geoip_module", return_value=GeoIP2Mock
    ):
        assert rule.test_user(request) is True
    assert GeoIP2Mock.mock_calls == [
        call(),
        call().country_code("123.120.0.2"),
    ]


@skip_if_geoip2_not_installed
@pytest.mark.django_db
def test_test_user_geoip_module_does_not_match(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="nl")
    request = rf.get("/", REMOTE_ADDR="123.120.0.2")
    GeoIP2Mock = MagicMock()
    GeoIP2Mock().configure_mock(**{"country_code.return_value": "SE"})
    GeoIP2Mock.reset_mock()
    with patch(
        "wagtail_personalisation.rules.get_geoip_module", return_value=GeoIP2Mock
    ):
        assert rule.test_user(request) is False
    assert GeoIP2Mock.mock_calls == [call(), call().country_code("123.120.0.2")]


@skip_if_geoip2_installed
@pytest.mark.django_db
def test_test_user_does_not_use_geoip_module_if_disabled(rf):
    segment = SegmentFactory(name="Test segment")
    rule = OriginCountryRuleFactory(segment=segment, country="se")
    request = rf.get("/", REMOTE_ADDR="123.120.0.2")
    assert rule.test_user(request) is False


@skip_if_geoip2_installed
def test_get_geoip_module_disabled():
    with pytest.raises(ImportError):
        from django.contrib.gis.geoip2 import GeoIP2  # noqa
    assert get_geoip_module() is None


@skip_if_geoip2_not_installed
def test_get_geoip_module_enabled():
    from django.contrib.gis.geoip2 import GeoIP2

    assert get_geoip_module() is GeoIP2
