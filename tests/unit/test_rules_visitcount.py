import pytest


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
