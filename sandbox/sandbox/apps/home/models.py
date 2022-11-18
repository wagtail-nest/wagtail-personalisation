from __future__ import absolute_import, unicode_literals

from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail import blocks
    from wagtail.admin.panels import FieldPanel
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
    if WAGTAIL_VERSION >= (3, 0):
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
    else:
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
            ]
        )

    content_panels = Page.content_panels + [
        FieldPanel("intro")
        if WAGTAIL_VERSION >= (3, 0)
        else RichTextFieldPanel("intro"),
        FieldPanel("body") if WAGTAIL_VERSION >= (3, 0) else StreamFieldPanel("body"),
    ]
