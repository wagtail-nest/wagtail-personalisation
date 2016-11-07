from django.conf import settings
from django.conf.urls import include, url
from django.core.urlresolvers import reverse
from wagtail.wagtailadmin import widgets
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from .models import Segment


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^segments/', include(admin_urls, app_name='segments', namespace='segments')),
    ]