import time

def impersonate_other_page(page, other_page):
    page.path = other_page.path
    page.depth = other_page.depth
    page.url_path = other_page.url_path
    page.title = other_page.title


def create_segment_dictionary(segment):
    return {
        "encoded_name": segment.encoded_name(),
        "id": segment.pk,
        "timestamp": int(time.time()),
        "persistent": segment.persistent
    }
