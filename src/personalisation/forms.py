from __future__ import absolute_import, unicode_literals

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from wagtail.wagtailcore.models import Page

from personalisation.models import Segment


class SegmentForm(forms.ModelForm):
    """
    Custom Segment form for the create view
    """
    class Meta:
        model = Segment
        fields = (
            'name',
            'status',
        )

    def __init__(self, *args, **kwargs):
        super(SegmentForm, self).__init__(*args, **kwargs)
