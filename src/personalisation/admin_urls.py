from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from personalisation import views

app_name = 'segment'
urlpatterns = [
    url(r'^segment/(\d+)/$', views.overview, name='overview'),
    # url(r'^segment/create/$', views.CreateSegmentView.as_view(), name='create'),
    url(r'^segment/(?P<segment_id>[0-9]+)/enable/$', views.enable, name='enable'),
    url(r'^segment/(?P<segment_id>[0-9]+)/disable/$', views.disable, name='disable'),
    # TODO: These might no longer be needed when using a modal
    url(r'^segment/time-rule/$', views.time_rule_embed, name="time_rule_embed"),
    url(r'^segment/referral-rule/$', views.referral_rule_embed, name="refferal_rule_embed"),
    url(r'^segment/visit-count-rule/$', views.visit_c_rule_embed, name="visit_count_rule_embed"),
]
