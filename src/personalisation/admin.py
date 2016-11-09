from django.contrib import admin

from personalisation import models


class TimeRuleAdminInline(admin.TabularInline):
    model = models.TimeRule
    extra = 0

class ReferralRuleAdminInline(admin.TabularInline):
    model = models.ReferralRule
    extra = 0

class VisitCountRuleAdminInline(admin.TabularInline):
    model = models.VisitCountRule
    extra = 0

class SegmentAdmin(admin.ModelAdmin):
    inlines = (TimeRuleAdminInline, ReferralRuleAdminInline, VisitCountRuleAdminInline)


admin.site.register(models.Segment, SegmentAdmin)
