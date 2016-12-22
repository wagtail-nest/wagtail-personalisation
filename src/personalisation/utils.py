def impersonate_other_page(page, other_page):
    page.path = other_page.path
    page.depth = other_page.depth
    page.url_path = other_page.url_path
    page.title = other_page.title
