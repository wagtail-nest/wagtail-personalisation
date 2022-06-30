from __future__ import absolute_import, unicode_literals

import datetime

import factory

from wagtail_personalisation import rules


class DayRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = rules.DayRule


class DeviceRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = rules.DeviceRule


class QueryRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = rules.QueryRule


class ReferralRuleFactory(factory.django.DjangoModelFactory):
    regex_string = "test.test"

    class Meta:
        model = rules.ReferralRule


class TimeRuleFactory(factory.django.DjangoModelFactory):
    start_time = datetime.time(8, 0, 0)
    end_time = datetime.time(23, 0, 0)

    class Meta:
        model = rules.TimeRule


class VisitCountRuleFactory(factory.django.DjangoModelFactory):
    operator = "more_than"
    count = 0

    class Meta:
        model = rules.VisitCountRule


class OriginCountryRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = rules.OriginCountryRule
