Creating a segment
==================

As soon as the installation is completed and configured, the module will be
visible in the Wagtail administrative area.

To create a segment, go to the "Segments" page and click on "Add a new segment".

On this page you will be presented with a form. Follow these steps to create a
new segment:

1. Enter a name for your segment.

2. (Optional) Select whether to match any or all defined rules.

    ``match any`` will result in a segment that is applied as soon as one of
    your rules matches the visitor. When ``match all`` is selected, all rules
    must match before the segment is applied.

3. (Optional) Set the segment persistence.

    When persistence is enabled, your segment will stick to the visitor once
    applied, even if the rules no longer match on the next visit.

4. Define your segment rules.

    Wagxperience comes with a basic set of :doc:`../default_rules` that allow
    you to get started quickly. The rules you define will be evaluated once a
    visitor makes a request to your application.

5. Save your segment.

    Click "save" to store your segment. It will be enabled by default,
    unless otherwise defined.
