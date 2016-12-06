from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from personalisation import views

app_name = 'segment'
urlpatterns = [
    url(r'^segment/(?P<segment_id>[0-9]+)/enable/$', views.enable,
        name='enable'),
    url(r'^segment/(?P<segment_id>[0-9]+)/disable/$', views.disable,
        name='disable'),
    url(r'^personalisation/(?P<page_id>[0-9]+)/copy/(?P<segment_id>[0-9]+)$',
        views.copy_page_view, name='copy_page')
]
