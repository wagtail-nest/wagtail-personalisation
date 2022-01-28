from __future__ import absolute_import, unicode_literals

import factory
from django.utils.text import slugify
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail_factories.factories import PageFactory

from tests.site.pages import models
from wagtail_personalisation.models import PersonalisablePageMetadata

try:
    if WAGTAIL_VERSION >= (3, 0):
        from wagtail.models import Locale
    else:
        from wagtail.core.models import Locale

    class LocaleFactory(factory.django.DjangoModelFactory):
        language_code = "en"

        class Meta:
            model = Locale

except ImportError:
    pass


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
