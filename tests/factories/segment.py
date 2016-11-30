import factory
from django.db import models
from personalisation.models import Segment, TimeRule


class SegmentFactory(factory.DjangoModelFactory):
    name = 'TestSegment'
    status = 'enabled'

    time_rule = factory.RelatedFactory(TimeRuleFactory, '%(app_label)s_%(class)s_related', action=TimeRule.ACTION_CREATE)

    class Meta:
        model = Segment


class TimeRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = TimeRule

