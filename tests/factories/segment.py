from __future__ import absolute_import, unicode_literals

import datetime

import factory

from personalisation import models


class SegmentFactory(factory.DjangoModelFactory):
    name = 'TestSegment'
    status = 'enabled'

    class Meta:
        model = models.Segment


class TimeRuleFactory(factory.DjangoModelFactory):
    start_time = datetime.time(8,0,0)
    end_time = datetime.time(23,0,0)

    class Meta:
        model = models.TimeRule

class ReferralRuleFactory(factory.DjangoModelFactory):
    regex_string = "test.test"

    class Meta:
        model = models.ReferralRule

class VisitCountRuleFactory(factory.DjangoModelFactory):
    operator = "more_than"
    count = 0

    class Meta:
        model = models.VisitCountRule


class QueryRuleFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.QueryRule
