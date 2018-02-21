import pytest

from tests.factories.rule import VisitCountRuleFactory
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
def test_visit_count(site, client):
    response = client.get('/')
    assert response.status_code == 200
    visit_count = client.session['visit_count']
    assert visit_count[0]['path'] == '/'
    assert visit_count[0]['count'] == 1

    response = client.get('/')
    assert response.status_code == 200
    visit_count = client.session['visit_count']
    assert visit_count[0]['path'] == '/'
    assert visit_count[0]['count'] == 2

    response = client.get('/page-1/')
    assert response.status_code == 200
    visit_count = client.session['visit_count']
    assert visit_count[0]['count'] == 2
    assert visit_count[1]['count'] == 1


@pytest.mark.django_db
def test_visit_count_call_test_user_with_user(site, client, user):
    segment = SegmentFactory(name='VisitCount')
    rule = VisitCountRuleFactory(counted_page=site.root_page, segment=segment)

    session = client.session
    session['visit_count'] = [{'path': '/', 'count': 2}]
    session.save()
    client.force_login(user)

    assert rule.test_user(None, user)


@pytest.mark.django_db
def test_visit_count_call_test_user_with_user_or_request_fails(site, client, user):
    segment = SegmentFactory(name='VisitCount')
    rule = VisitCountRuleFactory(counted_page=site.root_page, segment=segment)

    session = client.session
    session['visit_count'] = [{'path': '/', 'count': 2}]
    session.save()
    client.force_login(user)

    assert not rule.test_user(None)
