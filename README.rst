.. start-no-pypi

.. image:: https://readthedocs.org/projects/wagtail-personalisation/badge/?version=latest
    :target: https://readthedocs.org/projects/wagtail-personalisation/

.. image:: https://travis-ci.org/LabD/wagtail-personalisation.svg?branch=master
    :target: https://travis-ci.org/LabD/wagtail-personalisation

.. image:: http://codecov.io/github/LabD/wagtail-personalisation/coverage.svg?branch=master
    :target: http://codecov.io/github/LabD/wagtail-personalisation?branch=master

.. image:: https://img.shields.io/pypi/v/wagtail-personalisation.svg
    :target: https://pypi.python.org/pypi/wagtail-personalisation/

.. end-no-pypi

Wagtail personalisation
=======================

Wagtail personalisation enables simple content personalisation through
segmentation for the `Wagtail CMS`_.

.. _Wagtail CMS: http://wagtail.io/

.. image:: logo.png
   :scale: 50 %
   :alt: Wagxperience
   :align: center


.. image:: screenshot.png


Instructions
------------
To install the package with pip::

    pip install wagtail-personalisation

Next, include the ``wagtail_personalisation`` and
``wagtail.contrib.modeladmin`` app in your project's ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'wagtail.contrib.modeladmin',
        'wagtail_personalisation',
        # ...
    ]

Make sure that ``django.contrib.sessions.middleware.SessionMiddleware`` has
been added in first, this is a prerequisite for this project.


Changing segments adapter
-------------------------
To change the segments adapter, first make a new one based on the
``BaseSegmentsAdapter``

.. code-block:: python

    class YourSegmentsAdapter(BaseSegmentsAdapter):
        # Add your own logic here

Add the ``PERSONALISATION_SEGMENTS_ADAPTER`` setting to your settings.py and
choose your own adapter.


Sandbox
-------

To quickly experiment with the package you can use the sandbox provided in
the git repository. To install this you will need to create and activate a
virtualenv and then run ``make sandbox``. This will start a fresh wagtail
install with the personalisation module enabled on http://localhost:8000. The
superuser credentials are ``superuser@example.com`` with the password
``testing``.
