from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page

from wagtail_personalisation.models import PersonalisablePageMixin


class RegularPage(Page):
    subtitle = models.CharField(max_length=255, blank=True, default="")
    body = RichTextField(blank=True, default="")

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("body"),
    ]


class ContentPage(PersonalisablePageMixin, Page):
    subtitle = models.CharField(max_length=255, blank=True, default="")
    body = RichTextField(blank=True, default="")

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("body"),
    ]
