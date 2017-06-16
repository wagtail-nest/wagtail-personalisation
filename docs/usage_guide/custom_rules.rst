Creating custom rules
=====================

Rules consist of two important elements, the model's fields and the
``test_user`` function. They should inherit the ``AbstractBaseRule`` class from
``wagtail_personalisation.rules``.

A simple example of a rule could look something like this:

.. literalinclude:: ../../src/wagtail_personalisation/rules.py
   :pyobject: UserIsLoggedInRule

As you can see, the only real requirement is the ``test_user`` function that
will either return ``True`` or ``False`` based on the model's fields and
optionally the request object.

That's it!
