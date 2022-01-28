import pytest

from tests.factories.rule import VisitCountRuleFactory
from tests.factories.segment import SegmentFactory
from wagtail_personalisation.rules import VisitCountRule


@pytest.mark.django_db
def test_visit_count(site, client):
    response = client.get("/")
    assert response.status_code == 200
    visit_count = client.session["visit_count"]
    assert visit_count[0]["path"] == "/"
    assert visit_count[0]["count"] == 1

    response = client.get("/")
    assert response.status_code == 200
    visit_count = client.session["visit_count"]
    assert visit_count[0]["path"] == "/"
    assert visit_count[0]["count"] == 2

    response = client.get("/page-1/")
    assert response.status_code == 200
    visit_count = client.session["visit_count"]
    assert visit_count[0]["count"] == 2
    assert visit_count[1]["count"] == 1


@pytest.mark.django_db
def test_call_test_user_on_invalid_rule_fails(site, user, mocker):
    rule = VisitCountRule()
    assert not (rule.test_user(None, user))


@pytest.mark.django_db
def test_visit_count_call_test_user_with_user(site, client, user):
    segment = SegmentFactory(name="VisitCount")
    rule = VisitCountRuleFactory(counted_page=site.root_page, segment=segment)

    session = client.session
    session["visit_count"] = [{"path": "/", "count": 2}]
    session.save()
    client.force_login(user)

    assert rule.test_user(None, user)


@pytest.mark.django_db
def test_visit_count_call_test_user_with_user_or_request_fails(site, client, user):
    segment = SegmentFactory(name="VisitCount")
    rule = VisitCountRuleFactory(counted_page=site.root_page, segment=segment)

    session = client.session
    session["visit_count"] = [{"path": "/", "count": 2}]
    session.save()
    client.force_login(user)

    assert not rule.test_user(None)


@pytest.mark.django_db
def test_get_column_header(site):
    segment = SegmentFactory(name="VisitCount")
    rule = VisitCountRuleFactory(counted_page=site.root_page, segment=segment)

    assert rule.get_column_header() == "Visit count - Test page"


@pytest.mark.django_db
def test_get_user_info_string_returns_count(site, client, user):
    segment = SegmentFactory(name="VisitCount")
    rule = VisitCountRuleFactory(counted_page=site.root_page, segment=segment)

    session = client.session
    session["visit_count"] = [{"path": "/", "count": 2}]
    session.save()
    client.force_login(user)

    assert rule.get_user_info_string(user) == "2"
