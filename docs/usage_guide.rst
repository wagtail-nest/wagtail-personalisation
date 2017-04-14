Usage guide
===========

Creating a segment
------------------

As soon as the installation is completed and configured, the module will be visible in the Wagtail administrative area.

To create a segment, go to the "Segments" page. Click on "Add a new segment".

On this page you will be presented with a form. Follow the steps to create a segment:

1. Enter a name for your segment.

2. (Optional) Select whether to match any or all defined rules.

    ``match any`` will result in a segment that is applied as soon as one of your rules matches the visitor.
    When ``match all`` is selected, all rules must match before the segment is applied.

3. (Optional) Set the segment persistence.

    When persistence is enabled, your segment will stick to the visitor once applied, even if the rules no longer match on the next visit.

4. Define your segment rules.

    Wagxperience comes with a basic set of rules :doc:`default_rules` that allow you to get started quickly. The rules you define will be evaluated once a visitor makes a request to your application.

5. Save your segment.

    Click "save" to store your segment. It will be enabled by default, unless otherwise defined.


Creating content for your segment
---------------------------------

Once you've created a segment you can start serving these visitors with personalised content. To do this, you can go one of two directions.

1. Create a copy of a page for your segment.

2. Create StreamField blocks only visible to your segment.


Method 1: Create a copy
^^^^^^^^^^^^^^^^^^^^^^^

To create a copy from a page for a specific Segment (which you can change to your liking after copying it) simply go to the Explorer section and find the page you'd wish to personalize.

You'll notice a new "Variants" dropdown button has appeared. Click the button and select the segment you'd like to create personalized content for.

Once you've selected the segment, a copy of the page will be created with a title that includes the segment. Don't worry, you'r visitors won't be able to see this title.

You can change everything on this page you'd like. Visitors that are included in your segment, will automatically see the new page you've created for them.


Method 2: Create a block
^^^^^^^^^^^^^^^^^^^^^^^^

