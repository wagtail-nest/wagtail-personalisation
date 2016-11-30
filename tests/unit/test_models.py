import datetime

import pytest
from django.http import HttpRequest
from freezegun import freeze_time
from wagtail.wagtailcore.models import Site

from personalisation import models
from tests.factories.site import SiteFactory

"""Time Rule tests"""
@freeze_time("10:00:00")
def test_create_time_rule():
    time_rule = models.TimeRule(start_time=datetime.time(8, 0, 0), end_time=datetime.time(23, 0, 0))

    assert time_rule.test_user() is True

@freeze_time("10:00:00")
def test_time_rule_false():
    time_rule = models.TimeRule(start_time=datetime.time(11, 0, 0), end_time=datetime.time(23, 0, 0))

    assert time_rule.test_user() is False

@freeze_time("10:00:00")
def test_time_rule_reverse():
    time_rule = models.TimeRule(start_time=datetime.time(13, 0, 0), end_time=datetime.time(9, 0, 0))

    assert time_rule.test_user() is False

@freeze_time("10:00:00")
def test_time_rule_reverse_next_day():
    time_rule = models.TimeRule(start_time=datetime.time(11, 0, 0), end_time=datetime.time(11, 0, 0))

    assert time_rule.test_user() is False


"""Visit Count Rule tests"""
def test_visit_count_rule():
    visit_count_rule = models.VisitCountRule()


"""Test test"""
@pytest.mark.django_db
def test_test(rf):
    site = SiteFactory()

    request = HttpRequest()
    request.path = '/'
    request.META['HTTP_HOST'] = 'localhost'
    request.META['SERVER_PORT'] = 8000

    assert Site.find_for_request(request) == site
