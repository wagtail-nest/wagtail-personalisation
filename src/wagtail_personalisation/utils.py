import time

from django.utils import timezone


def impersonate_other_page(page, other_page):
    """Function to change the page metadata so the user gets to see the
    non-personalized path and page.

    :param page: The page to be impersonated
    :type page: wagtail_personalisation.models.PersonalisablePage
    :param other_page: The page it should impersonate
    :type other_page: wagtail_personalisation.models.PersonalisablePage

    """
    page.path = other_page.path
    page.depth = other_page.depth
    page.url_path = other_page.url_path
    page.title = other_page.title


def create_segment_dictionary(segment):
    """Creates a dictionary with all the required segment information.

    :param segment: Segment object
    :type segment: wagtail_personalisation.models.Segment
    :return: Dictionary with name, id, timestamp and persistent state.
    :rtype: dict

    """
    return {
        "encoded_name": segment.encoded_name(),
        "id": segment.pk,
        "timestamp": int(time.time()),
        "persistent": segment.persistent
    }


def count_active_days(enable_date, disable_date):
    """Return the number of days the segment has been active.

    :param enable_date: The date the segment was enabled
    :type enable_date: timezone.datetime
    :param disable_date: The date the segment was disabled
    :type disable_date: timezone.datetime
    :returns: The amount of days a segment is/has been active
    :rtype: int

    """
    if enable_date is not None:
        if disable_date is None or disable_date <= enable_date:
            # There is no disable date, or it is not relevant.
            delta = timezone.now() - enable_date
            return delta.days
        if disable_date > enable_date:
            # There is a disable date and it is relevant.
            delta = disable_date - enable_date
            return delta.days

    return 0
