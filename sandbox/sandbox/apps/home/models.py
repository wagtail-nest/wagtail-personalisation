from __future__ import absolute_import, unicode_literals

from wagtail.wagtailadmin.edit_handlers import RichTextFieldPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page

from wagtail_personalisation.models import PersonalisablePageMixin
from wagtail_personalisation.blocks import PersonalisedStructBlock


class HomePage(PersonalisablePageMixin, Page):
    intro = RichTextField()
    body = StreamField([
        ('personalisable_paragraph', PersonalisedStructBlock([
            ('paragraph', blocks.RichTextBlock()),
        ], icon='pilcrow'))
    ])

    content_panels = Page.content_panels + [
        RichTextFieldPanel('intro'),
        StreamFieldPanel('body'),
    ]
