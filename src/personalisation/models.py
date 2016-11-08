from __future__ import absolute_import, unicode_literals

import re
from datetime import datetime

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import InheritanceManager
from modelcluster.models import ClusterableModel
from wagtail.wagtailadmin.edit_handlers import FieldPanel


"""
Model for a new segment
"""
@python_2_unicode_compatible
class Segment(ClusterableModel):
    name = models.CharField(max_length=255)
    STATUS_CHOICES = (
        ('disabled', 'Disabled'),
        ('live', 'Live'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="disabled")

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    def encoded_name(self):
        return "".join(self.name.lower().split())


"""
Base for creating rules to segment users with
"""
@python_2_unicode_compatible
class AbstractBaseRule(models.Model):
    name = models.CharField(max_length=255)
    segment = models.ForeignKey(to=Segment, related_name="segment")
    objects = InheritanceManager()

    def test_user(self, request=None):
        return True

    def return_segment_id(self):
        return "".join(self.name.lower().split())

    def __str__(self):
        return self.name


"""
Time rule to segment users based on a start and end time
"""
@python_2_unicode_compatible
class TimeRule(AbstractBaseRule):
    start_time = models.TimeField(_("Starting time"))
    end_time = models.TimeField(_("Ending time"))

    def __init__(self, *args, **kwargs):
        super(TimeRule, self).__init__(*args, **kwargs)

    def test_user(self):
        current_time = self.get_current_time()
        starting_time = self.start_time
        ending_time = self.end_time

        return starting_time <= current_time <= ending_time

    def get_current_time(self):
        """Mockable function for testing purposes"""
        return datetime.now().time()


"""
Referral rule to segment users based on a regex test
"""
class ReferralRule(AbstractBaseRule):
    regex_string = models.TextField()

    def __init__(self, *args, **kwargs):
        super(ReferralRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        pattern = re.compile(re.escape(r'{0}').format(self.regex_string))
        return pattern.match(request.META.HTTP_REFERER)
