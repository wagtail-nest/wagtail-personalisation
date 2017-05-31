import pytest

from tests.factories.page import PageFactory
from tests.factories.segment import SegmentFactory
from tests.factories.site import SiteFactory


@pytest.fixture
def site():
    return SiteFactory()


@pytest.fixture
def segmented_page(site):
    page = PageFactory(parent=site.root_page)
    segment = SegmentFactory()
    return page.copy_for_segment(segment)
