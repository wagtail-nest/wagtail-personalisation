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

2. Add the module and ``wagtail.contrib.modeladmin`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        # ...
        'wagtail.contrib.modeladmin',
        'wagtail_personalisation',
        # ...
    ]

3. Update your database::

    python manage.py migrate

Continue reading: :doc:`implementation`
