from django.contrib import admin

from personalisation import models

class TimeRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')

class TimeRuleAdminInline(admin.TabularInline):
    model = models.TimeRule

class SegmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = (TimeRuleAdminInline,)


admin.site.register(models.TimeRule, TimeRuleAdmin)
admin.site.register(models.Segment, SegmentAdmin)
