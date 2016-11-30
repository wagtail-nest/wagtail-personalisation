import datetime

import pytest
from freezegun import freeze_time

from django.test.client import Client
from tests.factories.site import SiteFactory
from tests.factories.segment import SegmentFactory, TimeRuleFactory, ReferralRuleFactory

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

    def test_referral_segment(self, client):
        referral_segment = SegmentFactory(name='Referral')
        referral_rule = ReferralRuleFactory(
            regex_string="test.test",
            segment=referral_segment
        )

        client.get('/', **{ 'HTTP_REFERER': 'test.test'})

        assert client.session['segments'][0]['encoded_name'] == 'referral'
