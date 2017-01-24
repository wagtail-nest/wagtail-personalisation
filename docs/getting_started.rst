Getting started
===============


Installing Wagxperience
-----------------------

Installing the module
^^^^^^^^^^^^^^^^^^^^^

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

Including the middleware prerequisite
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure that ``django.contrib.sessions.middleware.SessionMiddleware`` is included in your ``MIDDLEWARE``::
    
    MIDDLEWARE = [
        # ...
        'django.contrib.sessions.middleware.SessionMiddleware',
        # ...
    ]

This is a prerequisite for this project.
