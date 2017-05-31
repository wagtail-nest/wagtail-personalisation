from __future__ import absolute_import, unicode_literals

import datetime

import pytest
from freezegun import freeze_time
from wagtail_factories import SiteFactory

from tests.factories.page import PageFactory
from tests.factories.rule import (
    DayRuleFactory, DeviceRuleFactory, QueryRuleFactory, ReferralRuleFactory,
    TimeRuleFactory, VisitCountRuleFactory)
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
class TestUserSegmenting(object):

    def setup(self):
        """
        Sets up a site root to test segmenting
        """
        self.site = SiteFactory(is_default_site=True)

    def test_no_segments(self, client):
        client.get('/')

        assert client.session['segments'] == []

    @freeze_time("10:00:00")
    def test_time_segment(self, client):
        time_only_segment = SegmentFactory(name='Time only')
        TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=time_only_segment)

        client.get('/')

        assert client.session['segments'][0]['encoded_name'] == 'time-only'

    @freeze_time("2017-01-01")
    def test_day_segment(self, client):
        day_only_segment = SegmentFactory(name='Day only')
        DayRuleFactory(
            sun=True,
            segment=day_only_segment)

        client.get('/')

        assert client.session['segments'][0]['encoded_name'] == 'day-only'

    def test_device_segment(self, client):
        device_only_segment = SegmentFactory(name='Device only')
        DeviceRuleFactory(
            tablet=True,
            segment=device_only_segment)

        client.get('/', **{'HTTP_USER_AGENT': 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X)'})

        assert client.session['segments'][0]['encoded_name'] == 'device-only'

    def test_device_segment_no_match(self, client):
        no_device_segment = SegmentFactory(name='No device')
        DeviceRuleFactory(
            mobile=True,
            segment=no_device_segment)

        client.get('/', **{'HTTP_USER_AGENT': 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X)'})

        assert not client.session['segments']

    def test_referral_segment(self, client):
        referral_segment = SegmentFactory(name='Referral')
        ReferralRuleFactory(
            regex_string="test.test",
            segment=referral_segment
        )

        client.get('/', **{'HTTP_REFERER': 'test.test'})

        assert client.session['segments'][0]['encoded_name'] == 'referral'

    @freeze_time("10:00:00")
    def test_time_and_referral_segment(self, client):
        segment = SegmentFactory(name='Both')
        TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=segment
        )
        ReferralRuleFactory(
            regex_string="test.test",
            segment=segment
        )

        client.get('/', **{'HTTP_REFERER': 'test.test'})

        assert client.session['segments'][0]['encoded_name'] == 'both'

    @freeze_time("7:00:00")
    def test_no_time_but_referral_segment(self, client):
        segment = SegmentFactory(name='Not both')
        TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=segment
        )
        ReferralRuleFactory(
            regex_string="test.test",
            segment=segment
        )

        client.get('/', **{'HTTP_REFERER': 'test.test'})

        assert len(client.session['segments']) == 0

    @freeze_time("9:00:00")
    def test_time_but_no_referral_segment(self, client):
        segment = SegmentFactory(name='Not both')
        TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=segment
        )
        ReferralRuleFactory(
            regex_string="test.test",
            segment=segment
        )

        client.get('/')

        assert len(client.session['segments']) == 0

    @freeze_time("9:00:00")
    def test_multiple_segments_exist(self, client):
        first_segment = SegmentFactory(name='First')
        second_segment = SegmentFactory(name='Second')

        TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=first_segment
        )
        ReferralRuleFactory(
            regex_string="test.test",
            segment=first_segment
        )

        TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=second_segment
        )

    def test_visit_count_rule(self, client):
        segment = SegmentFactory(name='Visit Count')

        VisitCountRuleFactory(
            counted_page=self.site.root_page,
            segment=segment
        )

        client.get("/root")

        # assert any(item['encoded_name'] == 'visit-count' for item in client.session['segments'])

    def test_query_rule(self, client):
        segment = SegmentFactory(name='Query')
        QueryRuleFactory(
            parameter="query",
            value="value",
            segment=segment,
        )

        client.get('/?query=value')

        assert any(item['encoded_name'] == 'query' for item in client.session['segments'])

    def test_only_one_query_rule(self, client):
        segment = SegmentFactory(name='Query')
        QueryRuleFactory(
            parameter="query",
            value="value",
            segment=segment
        )

        client.get('/?test=test&query=value')

        assert any(item['encoded_name'] == 'query' for item in client.session['segments'])

    def test_multiple_queries(self, client):
        segment = SegmentFactory(name='Multiple queries')
        QueryRuleFactory(
            parameter="test",
            value="test",
            segment=segment
        )

        QueryRuleFactory(
            parameter="query",
            value="value",
            segment=segment,
        )

        client.get('/?test=test&query=value')

        assert any(item['encoded_name'] == 'multiple-queries' for item in client.session['segments'])

    def test_persistent_segmenting(self, client):
        segment = SegmentFactory(name='Persistent', persistent=True)
        QueryRuleFactory(
            parameter="test",
            value="test",
            segment=segment
        )

        client.get('/?test=test')

        assert any(item['encoded_name'] == 'persistent' for item in client.session['segments'])

        client.get('/')

        assert any(item['encoded_name'] == 'persistent' for item in client.session['segments'])

    def test_non_persistent_segmenting(self, client):
        segment = SegmentFactory(name='Non Persistent')
        QueryRuleFactory(
            parameter="test",
            value="test",
            segment=segment
        )

        client.get('/?test=test')

        assert any(item['encoded_name'] == 'non-persistent' for item in client.session['segments'])

        client.get('/')

        assert not any(item['encoded_name'] == 'non-persistent' for item in client.session['segments'])

    def test_match_any_segmenting(self, client):
        segment = SegmentFactory(name='Match any', match_any=True)
        QueryRuleFactory(
            parameter='test',
            value='test',
            segment=segment,
        )
        QueryRuleFactory(
            parameter='test2',
            value='test2',
            segment=segment
        )

        client.get('/?test=test')

        assert any(item['encoded_name'] == 'match-any' for item in client.session['segments'])


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
