from django.contrib import admin

from personalisation import models


class TimeRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')

class TimeRuleAdminInline(admin.TabularInline):
    model = models.TimeRule

class ReferralRuleAdminInline(admin.TabularInline):
    model = models.ReferralRule

class VisitCountRuleAdminInline(admin.TabularInline):
    model = models.VisitCountRule

class SegmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = (TimeRuleAdminInline, ReferralRuleAdminInline, VisitCountRuleAdminInline)


admin.site.register(models.TimeRule, TimeRuleAdmin)
admin.site.register(models.Segment, SegmentAdmin)
