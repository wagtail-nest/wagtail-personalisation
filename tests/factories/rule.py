from __future__ import absolute_import, unicode_literals

import datetime

import factory

from wagtail_personalisation import rules


class DayRuleFactory(factory.DjangoModelFactory):

    class Meta:
        model = rules.DayRule


class DeviceRuleFactory(factory.DjangoModelFactory):

    class Meta:
        model = rules.DeviceRule


class QueryRuleFactory(factory.DjangoModelFactory):

    class Meta:
        model = rules.QueryRule


class ReferralRuleFactory(factory.DjangoModelFactory):
    regex_string = "test.test"

    class Meta:
        model = rules.ReferralRule


class TimeRuleFactory(factory.DjangoModelFactory):
    start_time = datetime.time(8, 0, 0)
    end_time = datetime.time(23, 0, 0)

    class Meta:
        model = rules.TimeRule


class VisitCountRuleFactory(factory.DjangoModelFactory):
    operator = "more_than"
    count = 0

    class Meta:
        model = rules.VisitCountRule
