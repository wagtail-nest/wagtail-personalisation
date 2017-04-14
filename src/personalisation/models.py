from __future__ import absolute_import, unicode_literals

import re
from datetime import datetime
from user_agents import parse

from django.db import models
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.utils.decorators import cached_classmethod
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, ObjectList,
    PageChooserPanel, TabbedInterface)
from wagtail.wagtailadmin.forms import WagtailAdminPageForm
from wagtail.wagtailcore.models import Page


@python_2_unicode_compatible
class AbstractBaseRule(models.Model):
    """Base for creating rules to segment users with"""
    segment = ParentalKey(
        'personalisation.Segment',
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss"
    )

    def test_user(self):
        """Test if the user matches this rule"""
        return True

    def __str__(self):
        return "Abstract segmentation rule"

    def encoded_name(self):
        """Returns a string with a slug for the rule"""
        return slugify(self.__str__().lower())

    def description(self):
        return "Abstract segmentation rule"

    class Meta:
        abstract = True


@python_2_unicode_compatible
class TimeRule(AbstractBaseRule):
    """Time rule to segment users based on a start and end time"""
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
    """Day rule to segment users based on day(s) of visit"""
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

        days = [
            self.mon, self.tue, self.wed, self.thu,
            self.fri, self.sat, self.sun
        ]

        return days[current_day]

    def __str__(self):
        return _('Day Rule')

    def description(self):
        days = {
            'mon': self.mon, 'tue': self.tue, 'wed': self.wed,
            'thu': self.thu, 'fri': self.fri, 'sat': self.sat,
            'sun': self.sun
        }

        chosen_days = [days[item] for item in days if days[item] is True]

        description = {
            'title': _('These users visit on'),
            'value': _('{}').format(", ".join(str(chosen_days))),
        }

        return description


@python_2_unicode_compatible
class ReferralRule(AbstractBaseRule):
    """Referral rule to segment users based on a regex test"""
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
    """Visit count rule to segment users based on amount of visits"""
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
    """Query rule to segment users based on matching queries"""
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
    """Device rule to segment users based on matching devices"""
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
    """User should be logged in"""
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default="enabled")
    persistent = models.BooleanField(
        default=False, help_text=_("Should the segment persist between visits?"))
    match_any = models.BooleanField(
        default=False,
        help_text=_("Should the segment match all the rules or just one of them?")
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('name', classname="title"),
            FieldRowPanel([
                FieldPanel('status'),
                FieldPanel('persistent'),
            ]),
            FieldPanel('match_any'),
        ], heading="Segment"),
        MultiFieldPanel([
            InlinePanel(
                "{}_related".format(rule._meta.db_table), 
                label=rule.__str__,
            ) for rule in AbstractBaseRule.__subclasses__()
        ], heading="Rules"),
    ]

    def __str__(self):
        return self.name

    def encoded_name(self):
        """Returns a string with a slug for the segment"""
        return slugify(self.name.lower())

    def get_rules(self):
        rules = AbstractBaseRule.__subclasses__()
        segment_rules = []
        for rule in rules:
            segment_rules += rule.objects.filter(segment=self)
        return segment_rules


def check_status_change(sender, instance, *args, **kwargs):
    """Check if the status has changed. Alter dates accordingly."""
    try:
        original_status = sender.objects.get(pk=instance.id).status
    except sender.DoesNotExist:
        original_status = ""

    if original_status != instance.status:
        if instance.status == "enabled":
            instance.enable_date = timezone.now()
            instance.visit_count = 0
            return instance
        if instance.status == "disabled":
            instance.disable_date = timezone.now()


pre_save.connect(check_status_change, sender=Segment)


class AdminPersonalisablePageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super(AdminPersonalisablePageForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        page = super(AdminPersonalisablePageForm, self).save(commit=False)

        if page.segment:
            segment = page.segment
            slug = "{}-{}".format(page.slug, segment.encoded_name())
            title = "{} ({})".format(page.title, segment.name)
            update_attrs = {
                'title': title,
                'slug': slug,
                'segment': segment,
                'live': False,
                'canonical_page': page,
                'is_segmented': True,
            }

            if page.is_segmented:
                slug = "{}-{}".format(
                    page.canonical_page.slug, segment.encoded_name())
                title = "{} ({})".format(
                    page.canonical_page.title, segment.name)
                page.slug = slug
                page.title = title
                page.save()
                return page
            else:
                new_page = page.copy(
                    update_attrs=update_attrs, copy_revisions=False)
                return new_page

        return page


class PersonalisablePage(Page):
    canonical_page = models.ForeignKey(
        'self', related_name='variations', on_delete=models.SET_NULL,
        blank=True, null=True
    )
    segment = models.ForeignKey(
        Segment, related_name='segments', on_delete=models.PROTECT,
        blank=True, null=True
    )
    is_segmented = models.BooleanField(default=False)

    variation_panels = [
        MultiFieldPanel([
            FieldPanel('segment'),
            PageChooserPanel('canonical_page', page_type=None),
        ])
    ]

    base_form_class = AdminPersonalisablePageForm

    def __str__(self):
        return "{}".format(self.title)

    @cached_property
    def has_variations(self):
        return self.variations.exists()

    @cached_property
    def is_canonical(self):
        return not self.canonical_page and self.has_variations


@cached_classmethod
def get_edit_handler(cls):
    tabs = []
    if cls.content_panels:
        tabs.append(ObjectList(cls.content_panels, heading=_("Content")))
    if cls.variation_panels:
        tabs.append(ObjectList(cls.variation_panels, heading=_("Variations")))
    if cls.promote_panels:
        tabs.append(ObjectList(cls.promote_panels, heading=_("Promote")))
    if cls.settings_panels:
        tabs.append(ObjectList(cls.settings_panels, heading=_("Settings"),
                               classname='settings'))

    edit_handler = TabbedInterface(tabs, base_form_class=cls.base_form_class)
    return edit_handler.bind_to_model(cls)


PersonalisablePage.get_edit_handler = get_edit_handler
