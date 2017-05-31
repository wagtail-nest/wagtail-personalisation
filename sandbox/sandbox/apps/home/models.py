from __future__ import absolute_import, unicode_literals

from wagtail.wagtailcore.models import Page

from wagtail_personalisation.models import PersonalisablePageMixin


class HomePage(PersonalisablePageMixin, Page):
    pass
