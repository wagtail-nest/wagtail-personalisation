Implementation
===============

Extending a page to be personalisable
-------------------------------------
Wagxperience offers a ``PersonalisablePage`` base class to extend from.
This is a standard ``Page`` class with personalisation options added.

Creating a new personalisable page
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Import and extend the ``personalisation.models.PersonalisablePage`` class to create a personalisable page.

A very simple example for a personalisable homepage::

    from wagtail_personalisation.models import PersonalisablePage

    class HomePage(PersonalisablePage):
        subtitle = models.CharField(max_length=255)
        body = RichTextField(blank=True, default='')

        content_panels = PersonalisablePage.content_panels + [
            FieldPanel('subtitle'),
            FieldPanel('body'),
        ]

It's just as simple as extending a standard ``Page`` class.

Migrating an existing page to be personalisable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Creating custom rules
---------------------

Rules consist of two important elements, the model's fields and the ``test_user`` function.

A very simple example of a rule would look something like this::

    from django.db import models
    from wagtail.wagtailadmin.edit_handlers import FieldPanel
    from personalisation import AbstractBaseRule

    class MyNewRule(AbstractBaseRule):
        field = models.BooleanField(default=False)

        panels = [
            FieldPanel('field'),
        ]

        def __init__(self, *args, **kwargs):
            super(MyNewRule, self).__init__(*args, **kwargs)

        def test_user(self, request):
            return self.field

As you can see, the only real requirement is the ``test_user`` function that will either return
``True`` or ``False`` based on the model's fields and optionally the request object.

Below is the "Time rule" model included with the module, which offers more complex functionality::

    @python_2_unicode_compatible
    class TimeRule(AbstractBaseRule):
        """Time rule to segment users based on a start and end time"""
        start_time = models.TimeField(_("Starting time"))
        end_time = models.TimeField(_("Ending time"))

        panels = [
            FieldRowPanel([
                FieldPanel('start_time'),
                FieldPanel('end_time'),
            ]),
        ]

        def __init__(self, *args, **kwargs):
            super(TimeRule, self).__init__(*args, **kwargs)

        def test_user(self, request=None):
            current_time = datetime.now().time()
            starting_time = self.start_time
            ending_time = self.end_time

            return starting_time <= current_time <= ending_time

        def __str__(self):
            return 'Time Rule'
