import time

from django.conf import settings
from django.db.models import F
from django.template.base import FilterExpression, kwarg_re
from django.utils import timezone
from django.utils.module_loading import import_string


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


def parse_tag(token, parser):
    """Parses template tag for name, arguments and keyword arguments.

    :param token: Template token containing all the tag contents
    :type token: django.template.base.Token
    :param parser: Template parser
    :type parser: django.template.base.Parser
    :return: Tuple with tag name, arguments and keyword arguments
    :rtype: tuple

    """
    # Split the tag content into words, respecting quoted strings.
    bits = token.split_contents()

    # Pull out the tag name.
    tag_name = bits.pop(0)

    # Parse the rest of the args, and build FilterExpressions from them so that
    # we can evaluate them later.
    args = []
    kwargs = {}
    for bit in bits:
        # Is this a kwarg or an arg?
        match = kwarg_re.match(bit)
        kwarg_format = match and match.group(1)
        if kwarg_format:
            key, value = match.groups()
            kwargs[key] = FilterExpression(value, parser)
        else:
            args.append(FilterExpression(bit, parser))

    return (tag_name, args, kwargs)


def exclude_variants(pages):
    """Checks if page is not a variant

    :param pages: Set of pages to check
    :type pages: QuerySet
    :return: Queryset of pages that aren't variants
    :rtype: QuerySet
    """
    from wagtail_personalisation.models import PersonalisablePageMetadata
    excluded_variant_pages = PersonalisablePageMetadata.objects.exclude(
        canonical_page_id=F('variant_id')
    ).values_list('variant_id')
    return pages.exclude(pk__in=excluded_variant_pages)


def can_delete_pages(pages, user):
    for variant in pages:
        if not variant.permissions_for_user(user).can_delete():
            return False
    return True


def get_client_ip(request):
    try:
        func = import_string(settings.WAGTAIL_PERSONALISATION_IP_FUNCTION)
    except AttributeError:
        pass
    else:
        return func(request)
    try:
        x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR']
        return x_forwarded_for.split(',')[-1].strip()
    except KeyError:
        return request.META['REMOTE_ADDR']
