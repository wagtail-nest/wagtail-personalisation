import pytest
from wagtail.wagtailcore.models import Page, Site


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # Remove some initial data that is brought by the sandbox module
        Site.objects.all().delete()
        Page.objects.all().exclude(depth=1).delete()
