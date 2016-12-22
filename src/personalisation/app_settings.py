from django.conf import settings
from django.utils.module_loading import import_string


segments_adapter = import_string(getattr(settings, 'PERSONALISATION_SEGMENTS_ADAPTER', 'personalisation.adapters.SessionSegmentsAdapter'))()

