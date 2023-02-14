import factory
from wagtail.models import Site

from tests.factories.page import ContentPageFactory


class SiteFactory(factory.django.DjangoModelFactory):
    hostname = "localhost"
    port = factory.Sequence(lambda n: 81 + n)
    site_name = "Test site"
    root_page = factory.SubFactory(ContentPageFactory, parent=None)
    is_default_site = False

    class Meta:
        model = Site
