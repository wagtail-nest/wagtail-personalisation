from django.contrib import admin

from personalisation import models
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline

class RulesInline(StackedPolymorphicInline):

    class TimeRuleAdminInline(StackedPolymorphicInline.Child):
        """Inline the Time Rule into the administration interface for segments"""
        model = models.TimeRule
        extra = 0


    class ReferralRuleAdminInline(StackedPolymorphicInline.Child):
        """
        Inline the Referral Rule into the administration interface for segments
        """
        model = models.ReferralRule
        extra = 0


    class VisitCountRuleAdminInline(StackedPolymorphicInline.Child):
        """
        Inline the Visit Count Rule into the administration interface for segments
        """
        model = models.VisitCountRule
        extra = 0


    model = models.AbstractBaseRule
    child_inlines = (
        TimeRuleAdminInline,
        ReferralRuleAdminInline,
        VisitCountRuleAdminInline,
    )


@admin.register(models.Segment)
class SegmentAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = (RulesInline,)
