from __future__ import absolute_import, unicode_literals

try:
    from django.contrib import admin
except ImportError:
    raise ImportError(
        'You are using the `wagtail_personalisation` app which requires the `django` module.'
        'Be sure to add `django` to your INSTALLED_APPS for `wagtail_personalisation` to work properly.'
)

from wagtail_personalisation import models, rules


class UserIsLoggedInRuleAdminInline(admin.TabularInline):
    """Inline the UserIsLoggedIn Rule into the
    administration interface for segments.

    """
    model = rules.UserIsLoggedInRule


class TimeRuleAdminInline(admin.TabularInline):
    """Inline the Time Rule into the
    administration interface for segments.

    """
    model = rules.TimeRule


class ReferralRuleAdminInline(admin.TabularInline):
    """Inline the Referral Rule into the
    administration interface for segments.

    """
    model = rules.ReferralRule


class VisitCountRuleAdminInline(admin.TabularInline):
    """Inline the Visit Count Rule into the
    administration interface for segments.

    """
    model = rules.VisitCountRule


class SegmentAdmin(admin.ModelAdmin):
    """Add the inline models to the Segment admin interface."""
    inlines = (UserIsLoggedInRuleAdminInline, TimeRuleAdminInline,
               ReferralRuleAdminInline, VisitCountRuleAdminInline)


admin.site.register(models.Segment, SegmentAdmin)
