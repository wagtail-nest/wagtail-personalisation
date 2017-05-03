import time


def impersonate_other_page(page, other_page):
    """
    Function to change the page metadata so the user gets to see the
    non-personalized path and page.
    :param page: The page to be impersonated
    :param other_page: The page it should impersonate
    """
    page.path = other_page.path
    page.depth = other_page.depth
    page.url_path = other_page.url_path
    page.title = other_page.title


def create_segment_dictionary(segment):
    """
    Creates a dictionary with all the required segment
    information.
    :param segment: Segment object
    :return: Dictionary with name, id, timestamp and persistent state.
    """
    return {
        "encoded_name": segment.encoded_name(),
        "id": segment.pk,
        "timestamp": int(time.time()),
        "persistent": segment.persistent
    }
