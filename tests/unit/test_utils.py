import pytest
from django.test import override_settings
from wagtail.core.models import Page as WagtailPage

from tests.factories.page import ContentPageFactory, PersonalisablePageMetadataFactory
from wagtail_personalisation.utils import (
    can_delete_pages,
    exclude_variants,
    get_client_ip,
    impersonate_other_page,
)

locale_factory = False

try:
    from tests.factories.page import LocaleFactory  # noqa

    locale_factory = True
except ImportError:
    pass


@pytest.fixture
def rootpage():
    return ContentPageFactory(parent=None, path="/", depth=0, title="root")


@pytest.fixture
def page(rootpage):
    return ContentPageFactory(parent=rootpage, path="/hi", title="Hi")


@pytest.fixture
def otherpage(rootpage):
    return ContentPageFactory(parent=rootpage, path="/bye", title="Bye")


@pytest.mark.django_db
def test_impersonate_other_page(page, otherpage):
    impersonate_other_page(page, otherpage)
    assert page.title == otherpage.title == "Bye"
    assert page.path == otherpage.path


@pytest.mark.django_db
def test_can_delete_pages_with_superuser(rf, user, segmented_page):
    user.is_superuser = True
    assert can_delete_pages([segmented_page], user)


@pytest.mark.django_db
def test_cannot_delete_pages_with_standard_user(user, segmented_page):
    assert not can_delete_pages([segmented_page], user)


def test_get_client_ip_with_remote_addr(rf):
    request = rf.get("/", REMOTE_ADDR="173.231.235.87")
    assert get_client_ip(request) == "173.231.235.87"


def test_get_client_ip_with_x_forwarded_for(rf):
    request = rf.get(
        "/", HTTP_X_FORWARDED_FOR="173.231.235.87", REMOTE_ADDR="10.0.23.24"
    )
    assert get_client_ip(request) == "173.231.235.87"


@override_settings(WAGTAIL_PERSONALISATION_IP_FUNCTION="some.non.existent.path")
def test_get_client_ip_custom_get_client_ip_function_does_not_exist(rf):
    with pytest.raises(ImportError):
        get_client_ip(rf.get("/"))


@override_settings(WAGTAIL_PERSONALISATION_IP_FUNCTION="tests.utils.get_custom_ip")
def test_get_client_ip_custom_get_client_ip_used(rf):
    assert get_client_ip(rf.get("/")) == "123.123.123.123"


def test_exclude_variants_with_pages_querysets():
    """
    Test that excludes variant works for querysets
    """
    for i in range(5):
        page = ContentPageFactory(
            path="/" + str(i), depth=0, url_path="/", title="Hoi " + str(i)
        )
        page.save()
    pages = WagtailPage.objects.all().specific().order_by("id")

    result = exclude_variants(pages)
    assert type(result) == type(pages)
    assert set(result.values_list("pk", flat=True)) == set(
        pages.values_list("pk", flat=True)
    )


def test_exclude_variants_with_pages_querysets_not_canonical():
    """
    Test that excludes variant works for querysets with
    personalisation_metadata canonical False
    """
    for i in range(5):
        page = ContentPageFactory(
            path="/" + str(i), depth=0, url_path="/", title="Hoi " + str(i)
        )
        page.save()
    pages = WagtailPage.objects.all().specific().order_by("id")
    # add variants
    for page in pages:
        variant = ContentPageFactory(title="variant %d" % page.pk)
        page.personalisation_metadata = PersonalisablePageMetadataFactory(
            canonical_page=page, variant=variant
        )
        page.save()

    pages = WagtailPage.objects.all().specific()
    result = exclude_variants(pages)
    assert type(result) == type(pages)
    assert result.count() < pages.count()


def test_exclude_variants_with_pages_querysets_meta_none():
    """
    Test that excludes variant works for querysets with meta as none
    """
    for i in range(5):
        page = ContentPageFactory(
            path="/" + str(i), depth=0, url_path="/", title="Hoi " + str(i)
        )
        page.save()
    pages = WagtailPage.objects.all().specific().order_by("id")
    # add variants
    for page in pages:
        page.personalisation_metadata = PersonalisablePageMetadataFactory(
            canonical_page=page, variant=page
        )
        page.save()

    pages = WagtailPage.objects.all().specific()
    result = exclude_variants(pages)
    assert type(result) == type(pages)
    assert set(result.values_list("pk", flat=True)) == set(
        pages.values_list("pk", flat=True)
    )
