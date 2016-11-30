import pytest

from tests.factories.site import SiteFactory
from tests.factories.segment import SegmentFactory

@pytest.mark.django_db
class TestUserSegmenting(object):

    def setup(self):
        """
        Sets up a user segment and a site root to test segmenting
        """
        self.standard_segment = SegmentFactory(name='Standard')
        self.time_only_segment = SegmentFactory(name='Time only')
        self.site = SiteFactory()


    def test_standard_segment(self, rf):
        request = rf.get('/')

        
