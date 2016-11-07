from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from modelcluster.models import ClusterableModel


"""
Model for a new segment
"""
@python_2_unicode_compatible
class Segment(ClusterableModel):
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name