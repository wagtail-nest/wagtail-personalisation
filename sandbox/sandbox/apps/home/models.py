from __future__ import absolute_import, unicode_literals

from wagtail.admin.edit_handlers import RichTextFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page

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
