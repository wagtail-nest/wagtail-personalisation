from django.conf.urls import url

from wagtail_personalisation import views

app_name = 'segment'

urlpatterns = [
    url(r'^segment/(?P<segment_id>[0-9]+)/toggle/$',
        views.toggle, name='toggle'),
    url(r'^(?P<page_id>[0-9]+)/copy/(?P<segment_id>[0-9]+)$',
        views.copy_page_view, name='copy_page'),
    url(r'^segment/toggle_segment_view/$',
        views.toggle_segment_view, name='toggle_segment_view'),
    url(r'^segment/users/(?P<segment_id>[0-9]+)$',
        views.segment_user_data, name='segment_user_data'),
]
