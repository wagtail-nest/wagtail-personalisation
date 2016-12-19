import importlib

def impersonate_other_page(page, other_page):
    page.path = other_page.path
    page.depth = other_page.depth
    page.url_path = other_page.url_path
    page.title = other_page.title

def import_class(name):
    module_name, class_name = name.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)
