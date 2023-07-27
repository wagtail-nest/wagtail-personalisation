import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.test.client import RequestFactory as BaseRequestFactory

from tests.factories.page import ContentPageFactory, RegularPageFactory
from tests.factories.segment import SegmentFactory
from tests.factories.site import SiteFactory


@pytest.fixture(scope="function")
def site():
    root_page = ContentPageFactory(parent=None, slug="")
    site = SiteFactory(is_default_site=True, root_page=root_page)

    page1 = ContentPageFactory(parent=root_page, slug="page-1")
    page2 = ContentPageFactory(parent=root_page, slug="page-2")
    ContentPageFactory(parent=page1, slug="page-1-1")
    ContentPageFactory(parent=page2, slug="page-2-1")

    RegularPageFactory(parent=root_page, slug="regular")
    return site


@pytest.fixture()
def segmented_page(site):
    page = ContentPageFactory(parent=site.root_page, slug="personalised")
    segment = SegmentFactory()
    return page.personalisation_metadata.copy_for_segment(segment)


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


@pytest.fixture()
def user(django_user_model):
    return django_user_model.objects.create(username="user")
