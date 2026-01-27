Installing Wagxperience
=======================

Wagtail Personalisation requires Wagtail_ 4.1+ and Django_ 3.2+

.. _Wagtail: https://github.com/wagtail/wagtail
.. _Django: https://github.com/django/django


To install the package with pip:

.. code-block:: console

    pip install wagtail-personalisation

Next, include the ``wagtail_personalisation``, ``'wagtail_modeladmin'``
(if the Wagtail version is 5.1 and above, otherwise ``'wagtail.contrib.modeladmin'``)
and ``wagtailfontawesomesvg`` apps in your project's ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'wagtail_modeladmin',          # if Wagtail >=5.1; Don't repeat if it's there already
        'wagtail.contrib.modeladmin',  # if Wagtail <5.1;  Don't repeat if it's there already
        'wagtail_personalisation',
        'wagtailfontawesomesvg',
        # ...
    ]

Make sure that ``django.contrib.sessions.middleware.SessionMiddleware`` has
been added in first, this is a prerequisite for this project.

.. code-block:: python

    MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        # ...
    ]


Configuring Available Rules (Optional)
---------------------------------------

By default, all built-in rules and any custom rules that inherit from
``AbstractBaseRule`` will be available in the Segment admin interface. If you
want to control which rules are available, you can specify them using the
``WAGTAIL_PERSONALISATION_RULES`` setting in your Django settings:

.. code-block:: python

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

If this setting is not specified, all rules will be available (default behavior).

The format for rule names is ``'app_label.ModelName'``. This is particularly useful
when:

- You want to exclude certain built-in rules that aren't relevant to your project
- You've created custom rules and want to ensure only specific rules are available
- You want to prevent unexpected custom rules from appearing automatically
