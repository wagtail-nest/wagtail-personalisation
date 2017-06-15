Creating personalized content
=============================

Once you've created a segment you can start serving these visitors with
personalised content. To do this, you can go one of two directions.

1. Create a copy of a page for your segment.

2. Create StreamField blocks only visible to your segment.

3. Create a template block only visible to your segment.


Method 1: Create a copy
^^^^^^^^^^^^^^^^^^^^^^^

To create a copy from a page for a specific Segment (which you can change to
your liking after copying it) simply go to the Explorer section and find the
page you'd wish to personalize.

You'll notice a new "Variants" dropdown button has appeared. Click the button
and select the segment you'd like to create personalized content for.

Once you've selected the segment, a copy of the page will be created with a
title that includes the segment. Don't worry, your visitors won't be able to
see this title.

You can change everything on this page you'd like. Visitors that are included in
your segment, will automatically see the new page you've created for them.


Method 2: Create a StreamField block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Method 3: Create a template block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can add a template block that only shows its contents to users of a
specific segment. This is done using the "segment" block.

When editing templates make sure to load the ``wagtail_personalisation_tags``
tags library in the template::

    {% load wagtail_personalisation_tags %}

After that you can add a template block with the name of the segment you want
the content to show up for::

    {% segment name="My Segment" %}
        <p>Only users within "My Segment" see this!</p>
    {% endsegment %}

The template block currently only supports one segment at a time. If you want
to target multiple segments you will have to make multiple blocks with the
same content.