from __future__ import absolute_import, unicode_literals

import factory
from wagtail.wagtailcore.models import Site

from tests.factories.page import SiteRootFactory


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = 8000
    site_name = 'Testing Site'
    root_page = factory.SubFactory(SiteRootFactory)
    is_default_site = True

    class Meta:
        model = Site
