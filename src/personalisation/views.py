from __future__ import absolute_import, unicode_literals

from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from wagtail.contrib.modeladmin.views import CreateView

from personalisation.forms import (ReferralRuleForm, SegmentForm, TimeRuleForm,
                                   VisitCountRuleForm)
from personalisation.models import (ReferralRule, Segment, TimeRule,
                                    VisitCountRule)


def overview(request):
    """Display segments overview. Dummy function"""
    return render(request, 'wagtailadmin/segment.html')

def enable(request, segment_id):
    """Enable the selected segment"""
    segment = get_object_or_404(Segment, pk=segment_id)
    segment.status = 'enabled'
    segment.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def disable(request, segment_id):
    """Disable the selected segment"""
    segment = get_object_or_404(Segment, pk=segment_id)
    segment.status = 'disabled'
    segment.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# TODO: Make these requestable from an existing page (the create page.)
# This code might become obselete.

def time_rule_embed(request):
    """Show the content of the time rule modal."""
    return render(request, 'wagtailadmin/embeds/time_rule.html', {
        'form': TimeRuleForm,
    })

def referral_rule_embed(request):
    """Show the content of the referral rule modal."""
    return render(request, 'wagtailadmin/embeds/referral_rule.html', {
        'form': ReferralRuleForm,
    })

def visit_c_rule_embed(request):
    """Show the content of the visit count rule modal."""
    return render(request, 'wagtailadmin/embeds/visit_count_rule.html', {
        'form': VisitCountRuleForm,
    })

class CreateSegmentView(CreateView):
    page_title = _("Add segment")
    form_class = SegmentForm
    template_name = 'modeladmin/personalisation/segment/create.html'
    header_icon = 'folder-open-1'
