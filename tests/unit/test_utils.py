from wagtail_personalisation.utils import impersonate_other_page, exclude_variants


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


class Metadata(object):
    def __init__(self, is_canonical=True):
        self.is_canonical = is_canonical


class PersonalisationMetadataPage(object):
    def __init__(self):
        self.personalisation_metadata = Metadata()


def test_exclude_variants_includes_pages_with_no_metadata_property():
    page = PersonalisationMetadataPage()
    del page.personalisation_metadata
    result = exclude_variants([page])
    assert result == [page]


def test_exclude_variants_includes_pages_with_metadata_none():
    page = PersonalisationMetadataPage()
    page.personalisation_metadata = None
    result = exclude_variants([page])
    assert result == [page]


def test_exclude_variants_includes_pages_with_metadata_canonical():
    page = PersonalisationMetadataPage()
    result = exclude_variants([page])
    assert result == [page]


def test_exclude_variants_excludes_pages_with_metadata_not_canonical():
    page = PersonalisationMetadataPage()
    page.personalisation_metadata.is_canonical = False
    result = exclude_variants([page])
    assert result == []
