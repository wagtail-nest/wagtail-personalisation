from __future__ import absolute_import, unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from wagtail.wagtailadmin.views import generic

from personalisation.models import Segment
from personalisation.forms import SegmentForm


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



