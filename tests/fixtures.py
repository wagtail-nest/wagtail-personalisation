import pytest

from tests.factories.page import PageFactory
from tests.factories.segment import SegmentFactory
from tests.factories.site import SiteFactory


@pytest.fixture(scope='function')
def site():
    site = SiteFactory(is_default_site=True)
    PageFactory(parent=site.root_page, slug='page-1')
    PageFactory(parent=site.root_page, slug='page-2')
    return site


@pytest.fixture
def segmented_page(site):
    page = PageFactory(parent=site.root_page)
    segment = SegmentFactory()
    return page.copy_for_segment(segment)
