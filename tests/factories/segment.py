from __future__ import absolute_import, unicode_literals

import factory

from wagtail_personalisation import models


class SegmentFactory(factory.django.DjangoModelFactory):
    name = "TestSegment"
    status = models.Segment.STATUS_ENABLED

    class Meta:
        model = models.Segment
