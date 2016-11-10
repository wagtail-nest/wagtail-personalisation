from django.template import Library
from django.utils import timezone

register = Library()

@register.filter(name='days_since')
def active_days(enable_date, disable_date):
    """Returns the number of days the segment has been active"""
    if enable_date is not None:
        if disable_date is None or (disable_date < enable_date):
            # There is no disable date, or it is not relevant.
            delta = timezone.now() - enable_date
            return delta.days
        if disable_date > enable_date:
            # There is a disable date and it is relevant.
            delta = disable_date - enable_date
            return delta.days
    return 0
