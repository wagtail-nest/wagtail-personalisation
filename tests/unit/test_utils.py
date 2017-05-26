import pytest

from wagtail_personalisation.utils import impersonate_other_page


class Page(object):
    def __init__(self, path, depth, url_path, title):
        self.path = path
        self.depth = depth
        self.url_path = url_path
        self.title = title

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def test_impersonate_other_page():
    page = Page(path="/", depth=0, url_path="/", title="Hoi")
    other_page = Page(path="/other", depth=1, url_path="/other", title="Doei")

    impersonate_other_page(page, other_page)

    assert page == other_page
