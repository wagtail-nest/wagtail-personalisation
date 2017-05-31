from __future__ import absolute_import, unicode_literals

import re
from datetime import datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey
from user_agents import parse
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, PageChooserPanel)


@python_2_unicode_compatible
class AbstractBaseRule(models.Model):
    """Base for creating rules to segment users with."""
    segment = ParentalKey(
        'wagtail_personalisation.Segment',
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss"
    )

    def test_user(self):
        """Test if the user matches this rule."""
        return True

    def __str__(self):
        return _('Abstract segmentation rule')

    def encoded_name(self):
        """Return a string with a slug for the rule."""
        return slugify(self.__str__().lower())

    def description(self):
        """Return a description explaining the functionality of the rule.
        Used in the segmentation dashboard.

        :returns: A dict containing a title and a value
        :rtype: dict

        """
        description = {
            'title': _('Abstract segmentation rule'),
            'value': _(''),
        }

        return description

    class Meta:
        abstract = True


@python_2_unicode_compatible
class TimeRule(AbstractBaseRule):
    """Time rule to segment users based on a start and end time.

    Matches when the time a request is made falls between the
    set start time and end time.

    """
    start_time = models.TimeField(_("Starting time"))
    end_time = models.TimeField(_("Ending time"))

    panels = [
        FieldRowPanel([
            FieldPanel('start_time'),
            FieldPanel('end_time'),
        ]),
    ]

    def __init__(self, *args, **kwargs):
        super(TimeRule, self).__init__(*args, **kwargs)

    def test_user(self, request=None):
        current_time = datetime.now().time()
        starting_time = self.start_time
        ending_time = self.end_time

        return starting_time <= current_time <= ending_time

    def __str__(self):
        return _('Time Rule')

    def description(self):
        description = {
            'title': _('These users visit between'),
            'value': _('{} and {}').format(
                self.start_time.strftime("%H:%M"),
                self.end_time.strftime("%H:%M")
            ),
        }

        return description


@python_2_unicode_compatible
class DayRule(AbstractBaseRule):
    """Day rule to segment users based on the day(s) of a visit.

    Matches when the day a request is made matches with the days
    set in the rule.

    """
    mon = models.BooleanField(_("Monday"), default=False)
    tue = models.BooleanField(_("Tuesday"), default=False)
    wed = models.BooleanField(_("Wednesday"), default=False)
    thu = models.BooleanField(_("Thursday"), default=False)
    fri = models.BooleanField(_("Friday"), default=False)
    sat = models.BooleanField(_("Saturday"), default=False)
    sun = models.BooleanField(_("Sunday"), default=False)

    panels = [
        FieldPanel('mon'),
        FieldPanel('tue'),
        FieldPanel('wed'),
        FieldPanel('thu'),
        FieldPanel('fri'),
        FieldPanel('sat'),
        FieldPanel('sun'),
    ]

    def __init__(self, *args, **kwargs):
        super(DayRule, self).__init__(*args, **kwargs)

    def test_user(self, request=None):
        current_day = datetime.today().weekday()

        days = [self.mon, self.tue, self.wed, self.thu,
                self.fri, self.sat, self.sun]

        return days[current_day]

    def __str__(self):
        return _('Day Rule')

    def description(self):
        days = {
            'mon': self.mon, 'tue': self.tue, 'wed': self.wed,
            'thu': self.thu, 'fri': self.fri, 'sat': self.sat,
            'sun': self.sun
        }

        chosen_days = []

        for key, value in days.items():
            if days[key]:
                chosen_days.append(key)

        description = {
            'title': _('These users visit on'),
            'value': (', '.join(_(day) for day in chosen_days)).title()
        }

        return description


@python_2_unicode_compatible
class ReferralRule(AbstractBaseRule):
    """Referral rule to segment users based on a regex test.

    Matches when the referral header in a request matches with
    the set regex test.

    """
    regex_string = models.TextField(
        _("Regex string to match the referer with"))

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
        return _('Referral Rule')

    def description(self):
        description = {
            'title': _('These visits originate from'),
            'value': _('{}').format(
                self.regex_string
            ),
            'code': True
        }

        return description


@python_2_unicode_compatible
class VisitCountRule(AbstractBaseRule):
    """Visit count rule to segment users based on amount of visits to a
    specified page.

    Matches when the operator and count validate True
    when visiting the set page.

    """
    OPERATOR_CHOICES = (
        ('more_than', _("More than")),
        ('less_than', _("Less than")),
        ('equal_to', _("Equal to")),
    )
    operator = models.CharField(max_length=20,
                                choices=OPERATOR_CHOICES, default="more_than")
    count = models.PositiveSmallIntegerField(default=0, null=True)
    counted_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
    )

    panels = [
        PageChooserPanel('counted_page'),
        FieldRowPanel([
            FieldPanel('operator'),
            FieldPanel('count'),
        ]),
    ]

    def __init__(self, *args, **kwargs):
        super(VisitCountRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        operator = self.operator
        segment_count = self.count

        # Local import for cyclic import
        from wagtail_personalisation.adapters import get_segment_adapter

        adapter = get_segment_adapter(request)

        visit_count = adapter.get_visit_count()
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
        return _('Visit count Rule')

    def description(self):
        description = {
            'title': _('These users visited {}').format(
                self.counted_page
            ),
            'value': _('{} {} times').format(
                self.get_operator_display(),
                self.count
            ),
        }

        return description


@python_2_unicode_compatible
class QueryRule(AbstractBaseRule):
    """Query rule to segment users based on matching queries.

    Matches when both the set parameter and value match with one
    present in the request query.

    """
    parameter = models.SlugField(_("The query parameter to search for"),
                                 max_length=20)
    value = models.SlugField(_("The value of the parameter to match"),
                             max_length=20)

    panels = [
        FieldPanel('parameter'),
        FieldPanel('value'),
    ]

    def __init__(self, *args, **kwargs):
        super(QueryRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        parameter = self.parameter
        value = self.value

        req_value = request.GET.get(parameter, '')
        if req_value == value:
            return True
        return False

    def __str__(self):
        return _('Query Rule')

    def description(self):
        description = {
            'title': _('These users used a url with the query'),
            'value': _('?{}={}').format(
                self.parameter,
                self.value
            ),
            'code': True
        }

        return description


@python_2_unicode_compatible
class DeviceRule(AbstractBaseRule):
    """Device rule to segment users based on matching devices.

    Matches when the set device type matches with the one present
    in the request user agent headers.

    """
    mobile = models.BooleanField(_("Mobile phone"), default=False)
    tablet = models.BooleanField(_("Tablet"), default=False)
    desktop = models.BooleanField(_("Desktop"), default=False)

    panels = [
        FieldPanel('mobile'),
        FieldPanel('tablet'),
        FieldPanel('desktop'),
    ]

    def __init__(self, *args, **kwargs):
        super(DeviceRule, self).__init__(*args, **kwargs)

    def test_user(self, request=None):
        ua_header = request.META['HTTP_USER_AGENT']
        user_agent = parse(ua_header)

        if user_agent.is_mobile:
            return self.mobile
        elif user_agent.is_tablet:
            return self.tablet
        elif user_agent.is_pc:
            return self.desktop
        else:
            return False

    def __str__(self):
        return _('Device Rule')


@python_2_unicode_compatible
class UserIsLoggedInRule(AbstractBaseRule):
    """User is logged in rule to segment users based on their authentication
    status.

    Matches when the user is authenticated.

    """
    is_logged_in = models.BooleanField(default=False)

    panels = [
        FieldPanel('is_logged_in'),
    ]

    def __init__(self, *args, **kwargs):
        super(UserIsLoggedInRule, self).__init__(*args, **kwargs)

    def test_user(self, request=None):
        return request.user.is_authenticated() == self.is_logged_in

    def __str__(self):
        return _('Logged In Rule')

    def description(self):
        status = _('Logged in')
        if self.is_logged_in is False:
            status = _('Not logged in')

        description = {
            'title': _('These visitors are'),
            'value': _('{}').format(
                status
            ),
        }

        return description
