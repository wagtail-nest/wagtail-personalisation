from django.conf import settings

from personalisation.utils import import_class


segments_adapter = import_class(getattr(settings, 'PERSONALISATION_SEGMENTS_ADAPTER', 'personalisation.adapters.SessionSegmentsAdapter'))()

