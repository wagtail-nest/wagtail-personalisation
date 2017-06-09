from __future__ import absolute_import, unicode_literals

import factory

from wagtail_personalisation import models


class SegmentFactory(factory.DjangoModelFactory):
    name = 'TestSegment'
    enabled = True

    class Meta:
        model = models.Segment
