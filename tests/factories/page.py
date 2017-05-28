from __future__ import absolute_import, unicode_literals

from wagtail_factories import PageFactory

from tests.sandbox.pages.models import HomePage
from wagtail_personalisation.models import PersonalisablePage


class PersonalisablePageFactory(PageFactory):
    class Meta:
        model = PersonalisablePage


class HomePageFactory(PageFactory):
    class Meta:
        model = HomePage
