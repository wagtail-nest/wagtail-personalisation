import pytest

from tests.factories.page import ContentPageFactory
from wagtail_personalisation.utils import impersonate_other_page


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
