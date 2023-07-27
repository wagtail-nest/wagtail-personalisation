import logging
import re
from importlib import import_module

import pycountry
from django.apps import apps
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.defaultfilters import slugify
from django.test.client import RequestFactory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from user_agents import parse
from wagtail.admin.panels import FieldPanel, FieldRowPanel

from wagtail_personalisation.utils import get_client_ip

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

logger = logging.getLogger(__name__)


def get_geoip_module():
    try:
        from django.contrib.gis.geoip2 import GeoIP2

        return GeoIP2
    except ImportError:
        logger.exception(
            "GeoIP module is disabled. To use GeoIP for the origin\n"
            "country personaliastion rule please set it up as per "
            "documentation:\n"
            "https://docs.djangoproject.com/en/stable/ref/contrib/gis/"
            "geoip2/.\n"
            "Wagtail-personalisation also works with Cloudflare and\n"
            "CloudFront country detection, so you should not see this\n"
            "warning if you use one of those."
        )


class AbstractBaseRule(models.Model):
    """Base for creating rules to segment users with."""

    icon = "fa-circle-o"
    static = False

    segment = ParentalKey(
        "wagtail_personalisation.Segment",
        related_name="%(app_label)s_%(class)ss",
    )

    class Meta:
        abstract = True
        verbose_name = "Abstract segmentation rule"

    def __str__(self):
        return str(self._meta.verbose_name)

    def test_user(self):
        """Test if the user matches this rule."""
        return True

    def encoded_name(self):
        """Return a string with a slug for the rule."""
        return slugify(str(self).lower())

    def description(self):
        """Return a description explaining the functionality of the rule.
        Used in the segmentation dashboard.

        :returns: A dict containing a title and a value
        :rtype: dict

        """
        description = {
            "title": _("Abstract segmentation rule"),
            "value": "",
        }

        return description

    @classmethod
    def get_descendant_models(cls):
        return [
            model for model in apps.get_models() if issubclass(model, AbstractBaseRule)
        ]


class TimeRule(AbstractBaseRule):
    """Time rule to segment users based on a start and end time.

    Matches when the time a request is made falls between the
    set start time and end time.

    """

    icon = "fa-clock-o"

    start_time = models.TimeField(_("Starting time"))
    end_time = models.TimeField(_("Ending time"))

    panels = [
        FieldRowPanel(
            [
                FieldPanel("start_time"),
                FieldPanel("end_time"),
            ]
        ),
    ]

    class Meta:
        verbose_name = _("Time Rule")

    def test_user(self, request=None):
        return self.start_time <= timezone.now().time() <= self.end_time

    def description(self):
        return {
            "title": _("These users visit between"),
            "value": _("{} and {}").format(
                self.start_time.strftime("%H:%M"), self.end_time.strftime("%H:%M")
            ),
        }


class DayRule(AbstractBaseRule):
    """Day rule to segment users based on the day(s) of a visit.

    Matches when the day a request is made matches with the days
    set in the rule.

    """

    icon = "fa-calendar-check-o"

    mon = models.BooleanField(_("Monday"), default=False)
    tue = models.BooleanField(_("Tuesday"), default=False)
    wed = models.BooleanField(_("Wednesday"), default=False)
    thu = models.BooleanField(_("Thursday"), default=False)
    fri = models.BooleanField(_("Friday"), default=False)
    sat = models.BooleanField(_("Saturday"), default=False)
    sun = models.BooleanField(_("Sunday"), default=False)

    panels = [
        FieldPanel("mon"),
        FieldPanel("tue"),
        FieldPanel("wed"),
        FieldPanel("thu"),
        FieldPanel("fri"),
        FieldPanel("sat"),
        FieldPanel("sun"),
    ]

    class Meta:
        verbose_name = _("Day Rule")

    def test_user(self, request=None):
        return [self.mon, self.tue, self.wed, self.thu, self.fri, self.sat, self.sun][
            timezone.now().date().weekday()
        ]

    def description(self):
        days = (
            ("mon", self.mon),
            ("tue", self.tue),
            ("wed", self.wed),
            ("thu", self.thu),
            ("fri", self.fri),
            ("sat", self.sat),
            ("sun", self.sun),
        )

        chosen_days = [day_name for day_name, chosen in days if chosen]

        return {
            "title": _("These users visit on"),
            "value": ", ".join([day for day in chosen_days]).title(),
        }


class ReferralRule(AbstractBaseRule):
    """Referral rule to segment users based on a regex test.

    Matches when the referral header in a request matches with
    the set regex test.

    """

    icon = "fa-globe"

    regex_string = models.TextField(_("Regular expression to match the referrer"))

    panels = [
        FieldPanel("regex_string"),
    ]

    class Meta:
        verbose_name = _("Referral Rule")

    def test_user(self, request):
        pattern = re.compile(self.regex_string)

        if "HTTP_REFERER" in request.META:
            referer = request.META["HTTP_REFERER"]
            if pattern.search(referer):
                return True
        return False

    def description(self):
        return {
            "title": _("These visits originate from"),
            "value": self.regex_string,
            "code": True,
        }


class VisitCountRule(AbstractBaseRule):
    """Visit count rule to segment users based on amount of visits to a
    specified page.

    Matches when the operator and count validate True
    when visiting the set page.

    """

    icon = "fa-calculator"
    static = True

    OPERATOR_CHOICES = (
        ("more_than", _("More than")),
        ("less_than", _("Less than")),
        ("equal_to", _("Equal to")),
    )
    operator = models.CharField(
        max_length=20, choices=OPERATOR_CHOICES, default="more_than"
    )
    count = models.PositiveSmallIntegerField(default=0, null=True)
    counted_page = models.ForeignKey(
        "wagtailcore.Page",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        FieldPanel("counted_page"),
        FieldRowPanel(
            [
                FieldPanel("operator"),
                FieldPanel("count"),
            ]
        ),
    ]

    class Meta:
        verbose_name = _("Visit count Rule")

    def _get_user_session(self, user):
        sessions = Session.objects.iterator()
        for session in sessions:
            session_data = session.get_decoded()
            if session_data.get("_auth_user_id") == str(user.id):
                return SessionStore(session_key=session.session_key)
        return SessionStore()

    def test_user(self, request, user=None):
        # Local import for cyclic import
        from wagtail_personalisation.adapters import (
            SEGMENT_ADAPTER_CLASS,
            SessionSegmentsAdapter,
            get_segment_adapter,
        )

        # Django formsets don't honour 'required' fields so check rule is valid
        try:
            self.counted_page
        except ObjectDoesNotExist:
            return False

        if user:
            # Create a fake request so we can use the adapter
            request = RequestFactory().get("/")
            request.user = user

            # If we're using the session adapter check for an active session
            if SEGMENT_ADAPTER_CLASS == SessionSegmentsAdapter:
                request.session = self._get_user_session(user)
            else:
                request.session = SessionStore()

        elif not request:
            # Return false if we don't have a user or a request
            return False

        operator = self.operator
        segment_count = self.count

        adapter = get_segment_adapter(request)

        visit_count = adapter.get_visit_count(self.counted_page)
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

    def description(self):
        return {
            "title": _("These users visited {}").format(self.counted_page),
            "value": _("{} {} times").format(self.get_operator_display(), self.count),
        }

    def get_column_header(self):
        return "Visit count - %s" % self.counted_page

    def get_user_info_string(self, user):
        # Local import for cyclic import
        from wagtail_personalisation.adapters import (
            SEGMENT_ADAPTER_CLASS,
            SessionSegmentsAdapter,
            get_segment_adapter,
        )

        # Create a fake request so we can use the adapter
        request = RequestFactory().get("/")
        request.user = user

        # If we're using the session adapter check for an active session
        if SEGMENT_ADAPTER_CLASS == SessionSegmentsAdapter:
            request.session = self._get_user_session(user)
        else:
            request.session = SessionStore()

        adapter = get_segment_adapter(request)
        visit_count = adapter.get_visit_count(self.counted_page)
        return str(visit_count)


class QueryRule(AbstractBaseRule):
    """Query rule to segment users based on matching queries.

    Matches when both the set parameter and value match with one
    present in the request query.

    """

    icon = "fa-link"

    parameter = models.SlugField(_("The query parameter to search for"), max_length=20)
    value = models.SlugField(_("The value of the parameter to match"), max_length=20)

    panels = [
        FieldPanel("parameter"),
        FieldPanel("value"),
    ]

    class Meta:
        verbose_name = _("Query Rule")

    def test_user(self, request):
        return request.GET.get(self.parameter, "") == self.value

    def description(self):
        return {
            "title": _("These users used a URL with the query"),
            "value": _("?{}={}").format(self.parameter, self.value),
            "code": True,
        }


class DeviceRule(AbstractBaseRule):
    """Device rule to segment users based on matching devices.

    Matches when the set device type matches with the one present
    in the request user agent headers.

    """

    icon = "fa-tablet"

    mobile = models.BooleanField(_("Mobile phone"), default=False)
    tablet = models.BooleanField(_("Tablet"), default=False)
    desktop = models.BooleanField(_("Desktop"), default=False)

    panels = [
        FieldPanel("mobile"),
        FieldPanel("tablet"),
        FieldPanel("desktop"),
    ]

    class Meta:
        verbose_name = _("Device Rule")

    def test_user(self, request=None):
        ua_header = request.META["HTTP_USER_AGENT"]
        user_agent = parse(ua_header)

        if user_agent.is_mobile:
            return self.mobile
        if user_agent.is_tablet:
            return self.tablet
        if user_agent.is_pc:
            return self.desktop
        return False


class UserIsLoggedInRule(AbstractBaseRule):
    """User is logged in rule to segment users based on their authentication
    status.

    Matches when the user is authenticated.

    """

    icon = "fa-user"

    is_logged_in = models.BooleanField(default=False)

    panels = [
        FieldPanel("is_logged_in"),
    ]

    class Meta:
        verbose_name = _("Logged in Rule")

    def test_user(self, request=None):
        return request.user.is_authenticated == self.is_logged_in

    def description(self):
        return {
            "title": _("These visitors are"),
            "value": _("Logged in") if self.is_logged_in else _("Not logged in"),
        }


COUNTRY_CHOICES = [
    (country.alpha_2.lower(), country.name) for country in pycountry.countries
]


class OriginCountryRule(AbstractBaseRule):
    """
    Test user against the country or origin of their request.

    Using this rule requires setting up GeoIP2 on Django or using
    CloudFlare or CloudFront geolocation detection.
    """

    country = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES,
        help_text=_(
            "Select origin country of the request that this rule will "
            "match against. This rule will only work if you use "
            "Cloudflare or CloudFront IP geolocation or if GeoIP2 "
            "module is configured."
        ),
    )

    class Meta:
        verbose_name = _("origin country rule")

    def get_cloudflare_country(self, request):
        """
        Get country code that has been detected by Cloudflare.

        Guide to the functionality:
        https://support.cloudflare.com/hc/en-us/articles/200168236-What-does-Cloudflare-IP-Geolocation-do-
        """
        try:
            return request.META["HTTP_CF_IPCOUNTRY"].lower()
        except KeyError:
            pass

    def get_cloudfront_country(self, request):
        try:
            return request.META["HTTP_CLOUDFRONT_VIEWER_COUNTRY"].lower()
        except KeyError:
            pass

    def get_geoip_country(self, request):
        GeoIP2 = get_geoip_module()
        if GeoIP2 is None:
            return False
        return GeoIP2().country_code(get_client_ip(request)).lower()

    def get_country(self, request):
        # Prioritise CloudFlare and CloudFront country detection over GeoIP.
        functions = (
            self.get_cloudflare_country,
            self.get_cloudfront_country,
            self.get_geoip_country,
        )
        for function in functions:
            result = function(request)
            if result:
                return result

    def test_user(self, request=None):
        return (self.get_country(request) or "") == self.country.lower()
