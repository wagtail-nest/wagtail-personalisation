import pytest

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.test.client import RequestFactory as BaseRequestFactory
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


@pytest.fixture()
def rf():
    """RequestFactory instance"""
    return RequestFactory()


class RequestFactory(BaseRequestFactory):

    def request(self, user=None, **request):
        request = super(RequestFactory, self).request(**request)
        request.user = AnonymousUser()
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        return request
