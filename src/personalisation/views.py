from __future__ import absolute_import, unicode_literals

from django.shortcuts import render


"""
Segments overview
"""
def overview(request):
    return render(request, 'wagtailadmin/segment.html')