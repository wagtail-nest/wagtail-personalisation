import factory
from django.utils.text import slugify
from wagtail.wagtailcore.models import Site
from wagtail_factories.factories import MP_NodeFactory

from tests.sandbox.pages.models import HomePage


class PageFactory(MP_NodeFactory):
    title = 'Test page'
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = HomePage


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = factory.Sequence(lambda n: 81 + n)
    site_name = 'Test site'
    root_page = factory.SubFactory(PageFactory, parent=None)
    is_default_site = False

    class Meta:
        model = Site
