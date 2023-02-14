from __future__ import absolute_import, unicode_literals

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from wagtail_personalisation.blocks import PersonalisedStructBlock
from wagtail_personalisation.models import PersonalisablePageMixin


class HomePage(PersonalisablePageMixin, Page):
    intro = RichTextField()
    body = StreamField(
        [
            (
                "personalisable_paragraph",
                PersonalisedStructBlock(
                    [
                        ("paragraph", blocks.RichTextBlock()),
                    ],
                    icon="pilcrow",
                ),
            )
        ],
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]
