from django.urls import re_path

from wagtail_personalisation import views

app_name = "segment"

urlpatterns = [
    re_path(r"^segment/(?P<segment_id>[0-9]+)/toggle/$", views.toggle, name="toggle"),
    re_path(
        r"^(?P<page_id>[0-9]+)/copy/(?P<segment_id>[0-9]+)$",
        views.copy_page_view,
        name="copy_page",
    ),
    re_path(
        r"^segment/toggle_segment_view/$",
        views.toggle_segment_view,
        name="toggle_segment_view",
    ),
    re_path(
        r"^segment/users/(?P<segment_id>[0-9]+)$",
        views.segment_user_data,
        name="segment_user_data",
    ),
]
