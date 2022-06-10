from __future__ import absolute_import, unicode_literals

from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail import blocks
    from wagtail.admin.panels import FieldPanel, RichTextFieldPanel
    from wagtail.fields import RichTextField, StreamField
    from wagtail.models import Page
else:
    from wagtail.admin.edit_handlers import RichTextFieldPanel, StreamFieldPanel
    from wagtail.core import blocks
    from wagtail.core.fields import RichTextField, StreamField
    from wagtail.core.models import Page

from wagtail_personalisation.blocks import PersonalisedStructBlock
from wagtail_personalisation.models import PersonalisablePageMixin


class HomePage(PersonalisablePageMixin, Page):
    intro = RichTextField()
    body = StreamField([
        ('personalisable_paragraph', PersonalisedStructBlock([
            ('paragraph', blocks.RichTextBlock()),
        ], icon='pilcrow'))
    ], use_json_field=True) if WAGTAIL_VERSION >= (3, 0) else StreamField([
        ('personalisable_paragraph', PersonalisedStructBlock([
            ('paragraph', blocks.RichTextBlock()),
        ], icon='pilcrow'))
    ])

    content_panels = Page.content_panels + [
        RichTextFieldPanel('intro'),
        FieldPanel('body'),
    ] if WAGTAIL_VERSION >= (3, 0) else Page.content_panels + [
        StreamFieldPanel('intro'),
        FieldPanel('body'),
    ]
