from __future__ import absolute_import, unicode_literals

import factory
from django.utils.text import slugify
from wagtail_factories.factories import MP_NodeFactory

from tests.site.pages.models import HomePage, SpecialPage


class HomePageFactory(MP_NodeFactory):
    title = 'Test page'
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = HomePage


class SpecialPageFactory(MP_NodeFactory):
    title = 'Test page'
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = SpecialPage
