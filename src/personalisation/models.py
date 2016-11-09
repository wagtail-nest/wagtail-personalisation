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
        ('enabled', 'Enabled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="enabled")

    panels = [
        FieldPanel('name'),
        FieldPanel('status'),
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
    segment = models.ForeignKey(to=Segment, related_name="segment")
    objects = InheritanceManager()

    def test_user(self, request=None):
        return True

    def __str__(self):
        return "Segmentation rule"


"""
Time rule to segment users based on a start and end time
"""
@python_2_unicode_compatible
class TimeRule(AbstractBaseRule):
    start_time = models.TimeField(_("Starting time"))
    end_time = models.TimeField(_("Ending time"))

    def __init__(self, *args, **kwargs):
        super(TimeRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        current_time = self.get_current_time()
        starting_time = self.start_time
        ending_time = self.end_time

        return starting_time <= current_time <= ending_time

    def get_current_time(self):
        """Mockable function for testing purposes"""
        return datetime.now().time()

    def __str__(self):
        return '{} - {}'.format(self.start_time, self.end_time)


"""
Referral rule to segment users based on a regex test
"""
class ReferralRule(AbstractBaseRule):
    regex_string = models.TextField()

    def __init__(self, *args, **kwargs):
        super(ReferralRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        pattern = re.compile(self.regex_string)

        if 'HTTP_REFERER' in request.META:
            referer = request.META['HTTP_REFERER']
            if pattern.search(referer):
                return True
        return False

    def __str__(self):
        return '{}'.format(self.regex_string)


"""
Visit count rule to segment users based on amount of visits
"""
class VisitCountRule(AbstractBaseRule):
    OPERATOR_CHOICES = (
        ('more_than', 'More than'),
        ('less_than', 'Less than'),
        ('equal_to', 'Equal to'),
    )
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, default="ht")
    count = models.PositiveSmallIntegerField(default=0)
    
    def __init__(self, *args, **kwargs):
        super(VisitCountRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        operator = self.operator
        segment_count = self.count
        visit_count = request.session.get('visit_count')

        if operator is "more_than":
            if visit_count > segment_count:
                return True
        elif operator is "less_than":
            if visit_count < segment_count:
                return True
        elif operator is "equal_to":
            if visit_count is segment_count:
                return True
        return False

    def __str__(self):
        operator_display = self.get_operator_display()
        return '{} {}'.format(operator_display, self.count)