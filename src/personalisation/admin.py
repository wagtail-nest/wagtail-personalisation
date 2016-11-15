from django.contrib import admin

from personalisation import models


class TimeRuleAdminInline(admin.TabularInline):
    """Inline the Time Rule into the administration interface for segments"""
    model = models.TimeRule
    extra = 0


class ReferralRuleAdminInline(admin.TabularInline):
    """
    Inline the Referral Rule into the administration interface for segments
    """
    model = models.ReferralRule
    extra = 0


class VisitCountRuleAdminInline(admin.TabularInline):
    """
    Inline the Visit Count Rule into the administration interface for segments
    """
    model = models.VisitCountRule
    extra = 0


class SegmentAdmin(admin.ModelAdmin):
    """Add the inlines to the Segment admin interface"""
    inlines = (
        TimeRuleAdminInline, ReferralRuleAdminInline,
        VisitCountRuleAdminInline
    )


admin.site.register(models.Segment, SegmentAdmin)
