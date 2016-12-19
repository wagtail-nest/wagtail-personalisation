from django.conf import settings

from personalisation.adapters import SessionSegmentsAdapter

settings_adapter = getattr(settings, 'PERSONALISATION_SEGMENTS_ADAPTER', SessionSegmentsAdapter)

segments_adapter = settings_adapter()
