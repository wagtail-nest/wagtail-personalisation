from __future__ import absolute_import, unicode_literals

import factory
from django.utils.text import slugify
from wagtail.models import Locale
from wagtail_factories.factories import PageFactory

from tests.site.pages import models
from wagtail_personalisation.models import PersonalisablePageMetadata


class LocaleFactory(factory.django.DjangoModelFactory):
    language_code = "en"

    class Meta:
        model = Locale


class ContentPageFactory(PageFactory):
    parent = None
    title = "Test page"
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = models.ContentPage


class RegularPageFactory(PageFactory):
    title = "Regular page"
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = models.RegularPage


class PersonalisablePageMetadataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PersonalisablePageMetadata
