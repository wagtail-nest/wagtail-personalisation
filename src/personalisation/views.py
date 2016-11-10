from __future__ import absolute_import, unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.modeladmin.views import CreateView

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


class CreateSegmentView(CreateView):
    page_title = _("Add segment")
    form_class = SegmentForm
    template_name = 'modeladmin/personalisation/segment/create.html'
    header_icon = 'folder-open-1'
