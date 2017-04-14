Included rules
==============

Time rule
---------

The time rule allows you to segment visitors based on the time of their visit.
Define a time frame in which visitors are matched to this segment.

==================  ==========================================================
Option              Description
==================  ==========================================================
Start time          The start time of your time frame.
End time            The end time of your time frame.
==================  ==========================================================

``personalisation.models.TimeRule``

Day rule
--------

The day rule allows you to segment visitors based on the day of their visit.
Select one or multiple days on which you'd like your segment to be applied.

==================  ==========================================================
Option              Description
==================  ==========================================================
Monday              Matches when the visitors visits on monday.
Tuesday             Matches when the visitors visits on tuesday.
Wednesday           Matches when the visitors visits on wednesday.
Thursday            Matches when the visitors visits on thursday.
Friday              Matches when the visitors visits on friday.
Saturday            Matches when the visitors visits on saturday.
Sunday              Matches when the visitors visits on sunday.
==================  ==========================================================

``personalisation.models.DayRule``

Referral rule
-------------

The referral rule allows you to match visitors based on the website they were
referred from. For example:

.. code-block:: bash

   example\.com|secondexample\.com|.*subdomain\.com

==================  ==========================================================
Option              Description
==================  ==========================================================
Regex string        The regex string to match the referral header to.
==================  ==========================================================

``personalisation.models.ReferralRule``
