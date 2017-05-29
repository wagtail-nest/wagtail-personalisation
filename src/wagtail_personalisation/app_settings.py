try:
    from django.conf import settings
    from django.utils.module_loading import import_string
except ImportError:
    raise ImportError(
        'You are using the `wagtail_personalisation` app which requires the `django` module.'
        'Be sure to add `django` to your INSTALLED_APPS for `wagtail_personalisation` to work properly.'
)

# Create a setting for the segments adapter to allow
# overwriting of the provided adapter's functionality.
segments_adapter = import_string(getattr(
    settings,
    'PERSONALISATION_SEGMENTS_ADAPTER',
    'wagtail_personalisation.adapters.SessionSegmentsAdapter'))()
