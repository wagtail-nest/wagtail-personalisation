Getting started
===============


Installing Wagxperience
-----------------------

The Wagxperience app runs in the Wagtail CMS. You can find out more here_.

.. _here: http://docs.wagtail.io/en/latest/getting_started/tutorial.html

1. Install the module::

    pip install wagtail-personalisation

2. Add the module and it's dependencies to your ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        # ...
        'wagtail.contrib.modeladmin',
        'personalisation',
        # ...
    ]

3. Update your database::

    python manage.py migrate

Make sure that ``django.contrib.sessions.middleware.SessionMiddleware`` has been added in first. This is a prerequisite for this project.


Creating your first segment
---------------------------

As soon as the installation is completed and configured, the module will be visible in the Wagtail administrative area.

To create a segment, go to the "Segments" page. Click on "Add a new segment".
