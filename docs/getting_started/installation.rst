Installing Wagxperience
=======================

Wagtail Personalisation requires Wagtail_ 4.1+ and Django_ 3.2+

.. _Wagtail: https://github.com/wagtail/wagtail
.. _Django: https://github.com/django/django


To install the package with pip:

.. code-block:: console

    pip install wagtail-personalisation

Next, include the ``wagtail_personalisation``, ``wagtail.contrib.modeladmin``
and ``wagtailfontawesome`` apps in your project's ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'wagtail.contrib.modeladmin',
        'wagtail_personalisation',
        'wagtailfontawesome',
        # ...
    ]

Make sure that ``django.contrib.sessions.middleware.SessionMiddleware`` has
been added in first, this is a prerequisite for this project.

.. code-block:: python

    MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        # ...
    ]
