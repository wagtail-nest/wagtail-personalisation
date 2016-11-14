from __future__ import absolute_import, unicode_literals

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from wagtail.wagtailcore.models import Page

from wagtail.wagtailadmin.forms import WagtailAdminModelForm

from personalisation.models import (ReferralRule, Segment, TimeRule,
                                    VisitCountRule)


class SegmentForm(forms.ModelForm):
    """Custom Segment form for the create view."""
    class Meta:
        """Why does this need a docstring? I do not know."""
        model = Segment
        fields = (
            'name',
            'status',
        )

class TimeRuleForm(WagtailAdminModelForm):
    """Create a form for the time rule model."""
    title = "Time"
    description = "Choose a time segment in which the user visits the site."
    class Meta:
        model = TimeRule
        fields = ['start_time', 'end_time']

class ReferralRuleForm(WagtailAdminModelForm):
    """Create a form for the referral rule model."""
    title = "Referrer"
    description = "Define a referring page, domain or query the user has to come from."
    class Meta:
        model = ReferralRule
        fields = ['regex_string']

class VisitCountRuleForm(WagtailAdminModelForm):
    """Create a form for the visit count rule model."""
    title = "Visit count"
    description = "Choose the number of visits the user has to have made."
    class Meta:
        model = VisitCountRule
        fields = ['operator', 'count']
