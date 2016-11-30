import factory

from personalisation.models import Segment, TimeRule


class SegmentFactory(factory.DjangoModelFactory):
    name = 'TestSegment'
    status = 'enabled'

    class Meta:
        model = Segment


class TimeRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = TimeRule
