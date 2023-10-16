from django.template import Library

from wagtail_personalisation.utils import count_active_days

register = Library()


@register.filter(name="days_since")
def active_days(enable_date, disable_date):
    return count_active_days(enable_date, disable_date)
