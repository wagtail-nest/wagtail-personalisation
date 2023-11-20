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
