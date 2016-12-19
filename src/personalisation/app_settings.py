from django.conf import settings

from personalisation.adapters import SessionSegmentsAdapter

segments_adapter = getattr(settings, 'PERSONALISATION_SEGMENTS_ADAPTER', SessionSegmentsAdapter)

