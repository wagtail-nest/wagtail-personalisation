from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from personalisation import views

app_name = 'segment'
urlpatterns = [
    url(r'^segment/(\d+)/$', views.overview, name='overview'),
    # url(r'^segment/create/$', views.CreateSegmentView.as_view(), name='create'),
    url(r'^segment/(?P<segment_id>[0-9]+)/enable/$', views.enable, name='enable'),
    url(r'^segment/(?P<segment_id>[0-9]+)/disable/$', views.disable, name='disable'),
]
