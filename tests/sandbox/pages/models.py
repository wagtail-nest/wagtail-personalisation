from __future__ import absolute_import, unicode_literals

from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page

from wagtail_personalisation.models import AbstractPersonalisablePage


class HomePage(AbstractPersonalisablePage, Page):
    subtitle = models.CharField(max_length=255)
    body = RichTextField(blank=True, default='')

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]
