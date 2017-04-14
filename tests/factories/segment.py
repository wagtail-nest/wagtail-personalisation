from __future__ import absolute_import, unicode_literals

import datetime

import factory

from personalisation import models, rules


class SegmentFactory(factory.DjangoModelFactory):
    name = 'TestSegment'
    status = 'enabled'

    class Meta:
        model = models.Segment


class TimeRuleFactory(factory.DjangoModelFactory):
    start_time = datetime.time(8, 0, 0)
    end_time = datetime.time(23, 0, 0)

    class Meta:
        model = rules.TimeRule


class DayRuleFactory(factory.DjangoModelFactory):

    class Meta:
        model = rules.DayRule


class ReferralRuleFactory(factory.DjangoModelFactory):
    regex_string = "test.test"

    class Meta:
        model = rules.ReferralRule


class VisitCountRuleFactory(factory.DjangoModelFactory):
    operator = "more_than"
    count = 0

    class Meta:
        model = rules.VisitCountRule


class QueryRuleFactory(factory.DjangoModelFactory):

    class Meta:
        model = rules.QueryRule

class DeviceRuleFactory(factory.DjangoModelFactory):

    class Meta:
        model = rules.DeviceRule
