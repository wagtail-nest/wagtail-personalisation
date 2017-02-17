from __future__ import absolute_import, unicode_literals

import factory
from wagtail.wagtailcore.models import Page
from wagtail_factories import PageFactory

from personalisation.models import PersonalisablePage
from tests.sandbox.pages.models import HomePage


class PersonalisablePageFactory(PageFactory):
    class Meta:
        model = PersonalisablePage


class HomePageFactory(PageFactory):
    class Meta:
        model = HomePage
