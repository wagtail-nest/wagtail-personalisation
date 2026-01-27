.. image:: https://raw.githubusercontent.com/wagtail-nest/wagtail-personalisation/refs/heads/main/logo.png
   :height: 261
   :width: 300
   :scale: 50
   :alt: Prism logo
   :align: center

Wagtail Personalisation
=======================

Wagtail Personalisation is a fully-featured personalisation module for
`Wagtail CMS`_. It enables editors to create customised pages
- or parts of pages - based on segments whose rules are configured directly
in the admin interface.

.. _Wagtail CMS: https://wagtail.org/


.. image:: https://raw.githubusercontent.com/wagtail-nest/wagtail-personalisation/refs/heads/main/docs/_static/images/segment_dashboard_view.png
    :alt: The segment dashboard view


Instructions
------------
Wagtail Personalisation requires Wagtail 6.3+ and Django 4.2+

To install the package with pip:

.. code-block:: console

    pip install wagtail-personalisation

Next, include the ``wagtail_personalisation``, ``'wagtail_modeladmin'``
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


Documentation
-------------

You can find more information about installing, extending and using this module
on `Read the Docs`_.

.. _Read the Docs: http://wagtail-personalisation.readthedocs.io


Sandbox
-------

To experiment with the package you can use the sandbox provided in
this repository. To install this you will need to create and activate a
virtualenv and then run ``make sandbox``. This will start a fresh Wagtail
install, with the personalisation module enabled, on http://localhost:8000
and http://localhost:8000/cms/. The superuser credentials are
``superuser@example.com`` with the password ``testing``.
