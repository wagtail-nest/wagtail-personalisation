from __future__ import absolute_import, unicode_literals

import factory
from django.utils.text import slugify
from wagtail_factories.factories import PageFactory

from tests.site.pages import models
from wagtail_personalisation.models import PersonalisablePageMetadata


class ContentPageFactory(PageFactory):
    parent = None
    title = 'Test page'
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = models.ContentPage


class RegularPageFactory(PageFactory):
    title = 'Regular page'
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = models.RegularPage


class PersonalisablePageMetadataFactory(factory.DjangoModelFactory):

    class Meta:
        model = PersonalisablePageMetadata
