from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from personalisation.models import Segment


"""
Segments overview
"""
def overview(request):
    return render(request, 'wagtailadmin/segment.html')

def enable(request, segment_id):
    segment = get_object_or_404(Segment, pk=segment_id)
    segment.status = 'enabled'
    segment.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def disable(request, segment_id):
    segment = get_object_or_404(Segment, pk=segment_id)
    segment.status = 'disabled'
    segment.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))