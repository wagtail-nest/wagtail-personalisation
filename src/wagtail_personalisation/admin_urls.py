from django.urls import include, path

from wagtail_personalisation import views

app_name = 'segment'

urlpatterns = [
    path("segment/<int:segment_id>/toggle/", views.toggle, name="toggle"),
    path("<int:page_id>/copy/<int:segment_id>/", views.copy_page_view, name="copy_page"),
    path("segment/toggle_segment_view/", views.toggle_segment_view, name="toggle_segment_view"),
    path("segment/users/<int:segment_id>/", views.segment_user_data, name="segment_user_data"),
]
