from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from personalisation import views

app_name = 'segment'
urlpatterns = [
    url(r'^segment/(\d+)/$', views.overview,
        name='overview'),
    url(r'^segment/(?P<segment_id>[0-9]+)/enable/$', views.enable,
        name='enable'),
    url(r'^segment/(?P<segment_id>[0-9]+)/disable/$', views.disable,
        name='disable'),
    url(r'^variations/(?P<page_pk>\d+)/add/(?P<segment_pk>[^/]+)/$',
        views.AddVariation.as_view(), name='add')
]
