import factory
from wagtail.wagtailcore.models import Page
from personalisation.models import PersonalisablePage

from tests.sandbox.pages.models import HomePage

class PersonalisablePageFactory(factory.DjangoModelFactory):
    class Meta:
        model = PersonalisablePage

    @classmethod
    def _create(cls, *args, **kwargs):
        obj = super(PersonalisablePageFactory, cls)._build(*args, **kwargs)
        if not obj.title:
            obj.title = "Page-Test"
        return obj
