from __future__ import absolute_import, unicode_literals

import re
from datetime import datetime

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel

from polymorphic.models import PolymorphicModel


@python_2_unicode_compatible
class Segment(ClusterableModel):
    """Model for a new segment"""
    name = models.CharField(max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    enable_date = models.DateTimeField(null=True, editable=False)
    disable_date = models.DateTimeField(null=True, editable=False)
    visit_count = models.PositiveIntegerField(default=0, editable=False)
    STATUS_CHOICES = (
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="enabled")

    panels = [
        FieldPanel('name'),
        FieldPanel('status'),
    ]

    def __str__(self):
        return self.name

    def encoded_name(self):
        """Returns a string with a slug for the segment"""
        return slugify(self.name.lower())


def check_status_change(sender, instance, *args, **kwargs):
    """Check if the status has changed. Alter dates accordingly."""
    try:
        original_status = sender.objects.get(pk=instance.id).status
    except sender.DoesNotExist:
        original_status = ""

    if original_status != instance.status:
        if instance.status == "enabled":
            instance.enable_date = datetime.now()
            instance.visit_count = 0
            return instance
        if instance.status == "disabled":
            instance.disable_date = datetime.now()

pre_save.connect(check_status_change, sender=Segment)


@python_2_unicode_compatible
class AbstractBaseRule(PolymorphicModel):
    """Base for creating rules to segment users with"""
    segment = ParentalKey('Segment', related_name="rules")

    def test_user(self, request):
        """Test if the user matches this rule"""
        return True

    def __str__(self):
        return "Segmentation rule"



@python_2_unicode_compatible
class TimeRule(AbstractBaseRule):
    """Time rule to segment users based on a start and end time"""
    start_time = models.TimeField(_("Starting time"))
    end_time = models.TimeField(_("Ending time"))

    panels = [
        FieldPanel('start_time'),
        FieldPanel('end_time'),
    ]

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


@python_2_unicode_compatible
class ReferralRule(AbstractBaseRule):
    """Referral rule to segment users based on a regex test"""
    regex_string = models.TextField(_("Regex string to match the referer with"))

    panels = [
        FieldPanel('regex_string'),
    ]

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


@python_2_unicode_compatible
class VisitCountRule(AbstractBaseRule):
    """Visit count rule to segment users based on amount of visits"""
    OPERATOR_CHOICES = (
        ('more_than', 'More than'),
        ('less_than', 'Less than'),
        ('equal_to', 'Equal to'),
    )
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, default="ht")
    count = models.PositiveSmallIntegerField(default=0, null=True)
    counted_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
    )

    panels = [
        FieldPanel('operator'),
        FieldPanel('count'),
        PageChooserPanel('counted_page'),
    ]

    def __init__(self, *args, **kwargs):
        super(VisitCountRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        operator = self.operator
        segment_count = self.count

        # TODO: Figure out a way to have a correct count before the middleware
        # initiates the test function

        def get_visit_count(request):
            """Search through the sessions to get the page visit count
            corresponding to the request."""
            for page in request.session['visit_count']:
                if page['path'] == request.path:
                    return page['count']

        visit_count = get_visit_count(request)

        if visit_count and operator == "more_than":
            if visit_count > segment_count:
                return True
        elif visit_count and operator == "less_than":
            if visit_count < segment_count:
                return True
        elif visit_count and operator == "equal_to":
            if visit_count == segment_count:
                return True
        return False

    def __str__(self):
        operator_display = self.get_operator_display()
        return '{} {}'.format(operator_display, self.count)
