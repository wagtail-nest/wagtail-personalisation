# Getting started

## Installation

Wagtail Personalisation requires [Wagtail](https://github.com/wagtail/wagtail) 7+ and [Django](https://github.com/django/django) 5.2+.

To install the package with pip:

```console
pip install wagtail-personalisation
```

Next, include the `wagtail_personalisation`, `wagtail_modeladmin` and `wagtailfontawesomesvg` apps in your project's `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'wagtail_modeladmin',  # Don't repeat if it's there already
    'wagtail_personalisation',
    'wagtailfontawesomesvg',
    # ...
]
```

Make sure that `django.contrib.sessions.middleware.SessionMiddleware` has been added in first, this is a prerequisite for this project.

```python
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ...
]
```

### Configuring available rules (optional)

By default, all built-in rules and any custom rules that inherit from `AbstractBaseRule` will be available in the Segment admin interface. If you want to control which rules are available, you can specify them using the `WAGTAIL_PERSONALISATION_RULES` setting in your Django settings:

```python
WAGTAIL_PERSONALISATION_RULES = [
    'wagtail_personalisation.TimeRule',
    'wagtail_personalisation.DayRule',
    'wagtail_personalisation.DeviceRule',
    'wagtail_personalisation.UserIsLoggedInRule',
    'wagtail_personalisation.QueryRule',
    'wagtail_personalisation.ReferralRule',
    'wagtail_personalisation.VisitCountRule',
    'wagtail_personalisation.OriginCountryRule',
    # Add your custom rules here
    'myapp.CustomRule',
]
```

If this setting is not specified, all rules will be available (default behavior).

The format for rule names is `'app_label.ModelName'`. This is particularly useful when:

- You want to exclude certain built-in rules that aren't relevant to your project
- You've created custom rules and want to ensure only specific rules are available
- You want to prevent unexpected custom rules from appearing automatically

## Using the sandbox

To experiment with the package you can use the sandbox provided in the [repository](https://github.com/wagtail-nest/wagtail-personalisation). It includes a couple of segments with rules, a personalisable page with a variant and a personalisable StreamField block.

To install this you will need to create and activate a virtualenv and then run `make sandbox`. This will start a fresh Wagtail install, with the personalisation module enabled, on http://localhost:8000 and http://localhost:8000/cms/. The superuser credentials are `superuser@example.com` with the password `testing`.
