Wagtail personalisation module
==============================

Personalisation module for Wagtail. This project is still work in progress.


Instructions
------------
To install the package with pip::

    pip install wagtail-personalisation

Next, include the ``personalisation``, ``polymorphic`` and ``wagtail.contrib.modeladmin`` app in your project's ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'wagtail.contrib.modeladmin',
        'polymorphic',
        'personalisation',
        # ...
    ]

Last but not least, add ``personalisation.middleware.SegmentMiddleware`` to your project's ``MIDDLEWARE``:

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'personalisation.middleware.SegmentMiddleware',
        # ...
    ]

Make sure that ``django.contrib.sessions.middleware.SessionMiddleware`` has been added in first, this is a prerequisite for this project.
