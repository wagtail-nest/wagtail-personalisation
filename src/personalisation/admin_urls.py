from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from personalisation import views

urlpatterns = [
    url(r'^segment/(\d+)/$', views.overview, name='overview'),
]
