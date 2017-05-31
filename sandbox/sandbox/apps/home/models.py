from __future__ import absolute_import, unicode_literals

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import RichTextFieldPanel
from wagtail.wagtailcore.fields import RichTextField

from wagtail_personalisation.models import PersonalisablePageMixin


class HomePage(PersonalisablePageMixin, Page):
    text_content = RichTextField()

    content_panels = Page.content_panels + [
        RichTextFieldPanel('text_content')
    ]
