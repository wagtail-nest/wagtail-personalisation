from __future__ import absolute_import, unicode_literals

import pytest
from freezegun import freeze_time
from wagtail_factories import SiteFactory

from tests.factories.rule import DayRuleFactory
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
class TestVisitPageView(object):

    def setup(self):
        """
        Sets up a site root to test segmenting
        """
        self.site = SiteFactory(is_default_site=True)

    def test_counts_visits(self, client):
        response = client.post('/visit-page/', {
            'page_id': 1,
            'path': 'foo',
        })

        assert response.status_code == 200
        assert client.session['visit_count'] == [
            {'slug': 'root', 'id': 1, 'path': 'foo', 'count': 1}
        ]

    @freeze_time("2017-01-01")
    def test_returns_segments(self, client):
        day_only_segment = SegmentFactory(name='Day only')
        DayRuleFactory(
            sun=True,
            segment=day_only_segment)

        response = client.post('/visit-page/', {
            'page_id': 1,
            'path': 'foo',
        })

        assert response.status_code == 200
        assert response.json() == {
            'segments': ['day-only']
        }

    def test_get_request(self, client):
        response = client.get('/visit-page/')

        assert response.status_code == 405

    def test_missing_page_id(self, client):
        response = client.post('/visit-page/')

        assert response.status_code == 400

    def test_missing_path(self, client):
        response = client.post('/visit-page/', {
            'page_id': 1,
        })

        assert response.status_code == 400

    def test_nonexistent_page(self, client):
        response = client.post('/visit-page/', {
            'page_id': 9999999,
            'path': 'foo',
        })

        assert response.status_code == 400
