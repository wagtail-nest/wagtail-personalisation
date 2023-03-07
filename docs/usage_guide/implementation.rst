Implementation
==============

Extending a page to be personalisable
-------------------------------------
Wagxperience offers a ``PersonalisablePage`` base class to extend from.
This is a standard ``Page`` class with personalisation options added.


Creating a new personalisable page
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Import and extend the ``personalisation.models.PersonalisablePage`` class to
create a personalisable page.

A very simple example for a personalisable homepage:

.. code-block:: python

    from wagtail.models import Page
    from wagtail_personalisation.models import PersonalisablePageMixin

    class HomePage(PersonalisablePageMixin, Page):
        pass

All you need is the ``PersonalisablePageMixin`` mixin and a Wagtail ``Page``
class of your liking.


.. _implementing_streamfield_blocks:

Adding personalisable StreamField blocks
----------------------------------------

Taking things a step further, you can also add personalisable StreamField blocks
to your page models. Below is the full Homepage model used in the sandbox.

.. literalinclude:: ../../sandbox/sandbox/apps/home/models.py


.. _implementing_template_blocks:

Using template blocks for personalisation
-----------------------------------------

*Please note that using the personalisable template tag is not the recommended
method for adding personalisation to your content, as it is largely decoupled
from the administration interface. Use responsibly.*

You can add a template block that only shows its contents to users of a
specific segment. This is done using the "segment" block.

When editing templates make sure to load the ``wagtail_personalisation_tags``
tags library in the template:

.. code-block:: jinja

    {% load wagtail_personalisation_tags %}

After that you can add a template block with the name of the segment you want
the content to show up for:

.. code-block:: jinja

    {% segment name="My Segment" %}
        <p>Only users within "My Segment" see this!</p>
    {% endsegment %}

The template block currently only supports one segment at a time. If you want
to target multiple segments you will have to make multiple blocks with the
same content.
