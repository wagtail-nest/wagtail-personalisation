from __future__ import absolute_import, unicode_literals

from wagtail.admin.edit_handlers import RichTextFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page

from wagtail_personalisation.blocks import (
    PersonalisedCharBlock, PersonalisedImageChooserBlock,
    PersonalisedRichTextBlock, PersonalisedStructBlock,
    PersonalisedTextBlock)
from wagtail_personalisation.models import PersonalisablePageMixin


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


class PersonalisedFieldsPage(Page):
    body = StreamField([
        ('personalised_block', PersonalisedStructBlock([
            ('heading', blocks.CharBlock()),
            ('paragraph', blocks.RichTextBlock())
        ], render_fields=['heading', 'paragraph'])),
        ('personalised_block_template', PersonalisedStructBlock([
            ('heading', blocks.CharBlock()),
            ('paragraph', blocks.RichTextBlock())
        ], template='blocks/personalised_block_template.html', label=_('Block with template'))),
        ('personalised_rich_text_block', PersonalisedRichTextBlock()),
        ('personalised_image', PersonalisedImageChooserBlock()),
        ('personalised_char', PersonalisedCharBlock()),
        ('personalised_text', PersonalisedTextBlock()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body')
    ]
