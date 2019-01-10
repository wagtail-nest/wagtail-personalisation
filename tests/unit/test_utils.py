from wagtail_personalisation.utils import (
    exclude_variants, impersonate_other_page)

from wagtail.core.models import Page as WagtailPage


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


def test_exclude_variants_with_pages_querysets():
    '''
    Test that excludes variant works for querysets too
    '''
    for i in range(5):
        page = WagtailPage(path="/" + str(i), depth=0, url_path="/", title="Hoi " + str(i))
        page.save()
    pages = WagtailPage.objects.all().order_by('id')

    result = exclude_variants(pages)
    assert type(result) == type(pages)
    assert result == pages


def test_exclude_variants_with_pages_querysets_not_canonical():
    '''
    Test that excludes variant works for querysets too
    '''
    for i in range(5):
        page = WagtailPage(path="/" + str(i), depth=0, url_path="/", title="Hoi " + str(i))
        page.save()
    pages = WagtailPage.objects.all().order_by('id')
    # add variants
    for page in pages:
        page.personalisation_metadata = Metadata(is_canonical=False)
        page.save()

    result = exclude_variants(pages)
    assert type(result) == type(pages)
    assert result.count() == 0


def test_exclude_variants_with_pages_querysets_meta_none():
    '''
    Test that excludes variant works for querysets too
    '''
    for i in range(5):
        page = WagtailPage(path="/" + str(i), depth=0, url_path="/", title="Hoi " + str(i))
        page.save()
    pages = WagtailPage.objects.all().order_by('id')
    # add variants
    for page in pages:
        page.personalisation_metadata = None
        page.save()

    result = exclude_variants(pages)
    assert type(result) == type(pages)
    assert result == pages
