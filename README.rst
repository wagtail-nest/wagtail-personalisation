.. image:: logo.png

Wagtail personalisation
=======================
Wagtail personalisation enables simple content personalisation through segmenting for Wagtail.


Instructions
------------
To install the package with pip::

    pip install wagtail-personalisation

Next, include the ``personalisation`` and ``wagtail.contrib.modeladmin`` app in your project's ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'wagtail.contrib.modeladmin',
        'personalisation',
        # ...
    ]

Make sure that ``django.contrib.sessions.middleware.SessionMiddleware`` has been added in first, this is a prerequisite for this project.

Changing segments adapter
-------------------------
To change the segments adapter, first make a new one based on the ``BaseSegmentsAdapter``

.. code-block:: python

    class YourSegmentsAdapter(BaseSegmentsAdapter):
        # Add your own logic here

Add the ``PERSONALISATION_SEGMENTS_ADAPTER`` setting to your settings.py and choose your own adapter.

Roadmap
-------------------------
.. image:: roadmap.png
