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


class HomePageFactory(factory.DjangoModelFactory):
    class Meta:
        model = HomePage

    @classmethod
    def build(cls, *args, **kwargs):
        obj = super(HomePageFactory, cls)._build(*args, **kwargs)

        for part in ('subtitle', 'body'):
            if not getattr(obj, part):
                setattr(obj, part, "{}".format(part))
        return obj


class SiteRootFactory(factory.DjangoModelFactory):
    title = 'site-root'
    depth = 2

    class Meta:
        model = Page

    @classmethod
    def _create(cls, *args, **kwargs):
        try:
            root = Page.objects.get(depth=0)
        except Page.DoesNotExist:
            root = Page.add_root(title='root')

        return root.add_child(title=kwargs['title'])
