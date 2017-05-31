import factory
from wagtail.wagtailcore.models import Site

from tests.factories.page import HomePageFactory


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = factory.Sequence(lambda n: 81 + n)
    site_name = 'Test site'
    root_page = factory.SubFactory(HomePageFactory, parent=None)
    is_default_site = False

    class Meta:
        model = Site
