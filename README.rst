.. start-no-pypi

.. image:: https://readthedocs.org/projects/wagtail-personalisation/badge/?version=latest
     :target: http://wagtail-personalisation.readthedocs.io/en/latest/?badge=latest

.. image:: https://travis-ci.org/LabD/wagtail-personalisation.svg?branch=master
    :target: https://travis-ci.org/LabD/wagtail-personalisation

.. image:: http://codecov.io/github/LabD/wagtail-personalisation/coverage.svg?branch=master
    :target: http://codecov.io/github/LabD/wagtail-personalisation?branch=master

.. image:: https://img.shields.io/pypi/v/wagtail-personalisation.svg
    :target: https://pypi.python.org/pypi/wagtail-personalisation/

.. end-no-pypi

Wagtail Personalisation
=======================

Wagtail Personalisation is a fully-featured personalisation module for `Wagtail CMS`_. It enables editors to create customised pages - or parts of pages - based on segments whose rules are configured directly in the admin interface.

.. _Wagtail CMS: http://wagtail.io/

.. image:: logo.png
   :scale: 50 %
   :alt: Wagxperience
   :align: center


.. image:: screenshot.png


Instructions
------------
Wagtail Personalisation requires Wagtail 1.10 and Django 1.11.

To install the package with pip::

    pip install wagtail-personalisation

Next, add the required apps in your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = [
        # Required apps
        'django.contrib.humanize',
        'wagtail.contrib.modeladmin',
        'wagtail_personalisation',
    ]

Make sure that ``django.contrib.sessions.middleware.SessionMiddleware`` has
been added in first, this is a prerequisite for this project.

Sandbox
-------

To experiment with the package you can use the sandbox provided in
this repository. To install this you will need to create and activate a
virtualenv and then run ``make sandbox``. This will start a fresh Wagtail
install, with the personalisation module enabled, on http://localhost:8000. The
superuser credentials are ``superuser@example.com`` with the password
``testing``.
