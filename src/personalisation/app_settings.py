from django.conf import settings
from django.utils.module_loading import import_string

# Create a setting for the segments adapter to allow
# overwriting of the provided adapter's functionality.
segments_adapter = import_string(getattr(
    settings,
    'PERSONALISATION_SEGMENTS_ADAPTER',
    'personalisation.adapters.SessionSegmentsAdapter'))()
