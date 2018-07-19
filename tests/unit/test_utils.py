import pytest

from tests.factories.page import ContentPageFactory
from wagtail_personalisation.utils import (
    can_delete_pages, impersonate_other_page)


@pytest.fixture
def rootpage():
    return ContentPageFactory(parent=None, path='/', depth=0, title='root')


@pytest.fixture
def page(rootpage):
    return ContentPageFactory(parent=rootpage, path='/hi', title='Hi')


@pytest.fixture
def otherpage(rootpage):
    return ContentPageFactory(parent=rootpage, path='/bye', title='Bye')


@pytest.mark.django_db
def test_impersonate_other_page(page, otherpage):
    impersonate_other_page(page, otherpage)
    assert page.title == otherpage.title == 'Bye'
    assert page.path == otherpage.path


@pytest.mark.django_db
def test_can_delete_pages_with_superuser(rf, user, segmented_page):
    user.is_superuser = True
    assert can_delete_pages([segmented_page], user)


@pytest.mark.django_db
def test_cannot_delete_pages_with_standard_user(user, segmented_page):
    assert not can_delete_pages([segmented_page], user)
