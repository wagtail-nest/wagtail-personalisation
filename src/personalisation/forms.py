from __future__ import absolute_import, unicode_literals

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from wagtail.wagtailcore.models import Page

from wagtail.wagtailadmin.forms import WagtailAdminModelForm

from personalisation.models import (
    ReferralRule, Segment, TimeRule, VisitCountRule, PersonalisablePage)


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


class PersonalisationForm(forms.Form):
    copy_from_canonical = forms.BooleanField(required=False)
    parent_page = forms.ModelChoiceField(
        queryset=PersonalisablePage.objects.all()
    )

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('page')
        self.site = self.page.get_site()
        self.segment = kwargs.pop('segment')
        self.base_fields['parent_page'].queryset = self.get_queryset()


        if self._page_has_required(self.page):
            self.base_fields['copy_from_canonical'].initial = True
            self.base_fields['copy_from_canonical'].disabled = True
            self.base_fields['copy_from_canonical'].help_text = _(
                "All fields need to be copied because of required fields"
            )

        super(PersonalisationForm, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = PersonalisablePage.objects.filter(segment=self.segment)
        allowed_pages = [p.pk for p in qs if (
            self.page.can_move_to(p) and p.get_site() == self.site
        )]
        qs = PersonalisablePage.objects.filter(pk__in=allowed_pages)
        if not qs:
            return Page.objects.filter(pk=self.site.root_page.pk)
        return qs


    def _page_has_required(self, page):
        common_fields = set(PersonalisablePage._meta.fields)
        specific_fields = set(page.specific._meta.fields) - common_fields

        required_fields = [f for f in specific_fields
                           if not f.blank and not f.name.endswith('ptr')]

        if required_fields:
            return True
        return False
