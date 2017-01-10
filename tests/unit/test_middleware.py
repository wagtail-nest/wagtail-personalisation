from __future__ import absolute_import, unicode_literals

import datetime

import pytest
from django.test.client import Client
from freezegun import freeze_time
from wagtail.wagtailcore.models import Page

from tests.factories.segment import (
    QueryRuleFactory, ReferralRuleFactory, SegmentFactory, TimeRuleFactory,
    DayRuleFactory, VisitCountRuleFactory)
from tests.factories.site import SiteFactory


@pytest.mark.django_db
class TestUserSegmenting(object):

    def setup(self):
        """
        Sets up a site root to test segmenting
        """
        self.site = SiteFactory()

    def test_no_segments(self, client):
        request = client.get('/')

        assert client.session['segments'] == []

    @freeze_time("10:00:00")
    def test_time_segment(self, client):
        time_only_segment = SegmentFactory(name='Time only')
        time_rule = TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=time_only_segment)

        request = client.get('/')

        assert client.session['segments'][0]['encoded_name'] == 'time-only'


    @freeze_time("2017-01-01")
    def test_day_segment(self, client):
        day_only_segment = SegmentFactory(name='Day only')
        day_rule = DayRuleFactory(
            sun=True,
            segment=day_only_segment)

        request = client.get('/')

        assert client.session['segments'][0]['encoded_name'] == 'day-only'


    def test_referral_segment(self, client):
        referral_segment = SegmentFactory(name='Referral')
        referral_rule = ReferralRuleFactory(
            regex_string="test.test",
            segment=referral_segment
        )

        client.get('/', **{ 'HTTP_REFERER': 'test.test'})

        assert client.session['segments'][0]['encoded_name'] == 'referral'

    @freeze_time("10:00:00")
    def test_time_and_referral_segment(self, client):
        segment = SegmentFactory(name='Both')
        time_rule = TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=segment
        )
        referral_rule = ReferralRuleFactory(
            regex_string="test.test",
            segment=segment
        )

        client.get('/', **{ 'HTTP_REFERER': 'test.test'})

        assert client.session['segments'][0]['encoded_name'] == 'both'

    @freeze_time("7:00:00")
    def test_no_time_but_referral_segment(self, client):
        segment = SegmentFactory(name='Not both')
        time_rule = TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=segment
        )
        referral_rule = ReferralRuleFactory(
            regex_string="test.test",
            segment=segment
        )

        client.get('/', **{ 'HTTP_REFERER': 'test.test'})

        assert len(client.session['segments']) == 0

    @freeze_time("9:00:00")
    def test_time_but_no_referral_segment(self, client):
        segment = SegmentFactory(name='Not both')
        time_rule = TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=segment
        )
        referral_rule = ReferralRuleFactory(
            regex_string="test.test",
            segment=segment
        )

        client.get('/')

        assert len(client.session['segments']) == 0

    @freeze_time("9:00:00")
    def test_multiple_segments_exist(self, client):
        first_segment = SegmentFactory(name='First')
        second_segment = SegmentFactory(name='Second')

        first_segment_time_rule = TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=first_segment
        )
        first_segment_referral_rule = ReferralRuleFactory(
            regex_string="test.test",
            segment=first_segment
        )

        second_segment_time_rule = TimeRuleFactory(
            start_time=datetime.time(8, 0, 0),
            end_time=datetime.time(23, 0, 0),
            segment=second_segment
        )

        second_segment_referral_rule = ReferralRuleFactory


    def test_visit_count_rule(self, client):
        segment = SegmentFactory(name='Visit Count')

        visit_count_rule = VisitCountRuleFactory(
            counted_page=Page.objects.filter(slug="root").first(),
            segment=segment
        )

        client.get("/root")

        # assert any(item['encoded_name'] == 'visit-count' for item in client.session['segments'])

    def test_query_rule(self, client):
        segment = SegmentFactory(name='Query')
        query_rule = QueryRuleFactory(
            parameter="query",
            value="value",
            segment=segment,
        )

        client.get('/?query=value')

        assert any(item['encoded_name'] == 'query' for item in client.session['segments'])

    def test_only_one_query_rule(self, client):
        segment = SegmentFactory(name='Query')
        query_rule = QueryRuleFactory(
            parameter="query",
            value="value",
            segment=segment
        )

        client.get('/?test=test&query=value')

        assert any(item['encoded_name'] == 'query' for item in client.session['segments'])

    def test_multiple_queries(self, client):
        segment = SegmentFactory(name='Multiple queries')
        first_query_rule = QueryRuleFactory(
            parameter="test",
            value="test",
            segment=segment
        )

        second_query_rule = QueryRuleFactory(
            parameter="query",
            value="value",
            segment=segment,
        )

        client.get('/?test=test&query=value')

        assert any(item['encoded_name'] == 'multiple-queries' for item in client.session['segments'])


    def test_persistent_segmenting(self, client):
        segment = SegmentFactory(name='Persistent', persistent=True)
        query_rule = QueryRuleFactory(
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
        query_rule = QueryRuleFactory(
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
        query_rule = QueryRuleFactory(
            parameter='test',
            value='test',
            segment=segment,
        )
        second_query_rule = QueryRuleFactory(
            parameter='test2',
            value='test2',
            segment=segment
        )

        client.get('/?test=test')
        
        assert any(item['encoded_name'] == 'match-any' for item in client.session['segments'])

@pytest.mark.django_db
class TestUserVisitCount(object):

    def setup(self):
        self.site = SiteFactory()

        # TODO: Set up a bunch of pages for testing the visit count

    def test_visit_count(self, client):
        client.get('/')

        assert any(item['path'] == '/' for item in client.session['visit_count'])

    def test_no_visit_count(self, client):
        client.get('/')

        assert not any(item['path'] == '/doesntexist' for item in client.session['visit_count'])
