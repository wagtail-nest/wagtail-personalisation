from __future__ import absolute_import, unicode_literals

try:
    from django.conf.urls import url
except ImportError:
    raise ImportError(
        'You are using the `wagtail_personalisation` app which requires the `django` module.'
        'Be sure to add `django` to your INSTALLED_APPS for `wagtail_personalisation` to work properly.'
)

from wagtail_personalisation import views

app_name = 'segment'

urlpatterns = [
    url(r'^segment/(?P<segment_id>[0-9]+)/toggle/$',
        views.toggle, name='toggle'),
    url(r'^(?P<page_id>[0-9]+)/copy/(?P<segment_id>[0-9]+)$',
        views.copy_page_view, name='copy_page')
]
