import factory
from wagtail.wagtailcore.models import Site

class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = 8000
    site_name = 'Testing Site'
    is_default_site = True

    class Meta
        model = Site
