from __future__ import absolute_import, unicode_literals

import factory

from personalisation import models


class SegmentFactory(factory.DjangoModelFactory):
    name = 'TestSegment'
    status = 'enabled'

    class Meta:
        model = models.Segment
