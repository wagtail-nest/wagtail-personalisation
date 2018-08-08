Included rules
==============

Wagxperience comes with a base set of rules that allow you to start segmenting
your visitors quickly.


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

``wagtail_personalisation.rules.TimeRule``


Day rule
--------

The day rule allows you to segment visitors based on the day of their visit.
Select one or multiple days on which you would like your segment to be applied.

==================  ==========================================================
Option              Description
==================  ==========================================================
Monday              Matches when the visitors visits on a monday.
Tuesday             Matches when the visitors visits on a tuesday.
Wednesday           Matches when the visitors visits on a wednesday.
Thursday            Matches when the visitors visits on a thursday.
Friday              Matches when the visitors visits on a friday.
Saturday            Matches when the visitors visits on a saturday.
Sunday              Matches when the visitors visits on a sunday.
==================  ==========================================================

``wagtail_personalisation.rules.DayRule``


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

``wagtail_personalisation.rules.ReferralRule``


Visit count rule
----------------

The visit count rule allows you to segment a visitor based on the amount of
visits per page. Use the operator to to set a maximum, minimum or equal
amount of visits.

==================  ==========================================================
Option              Description
==================  ==========================================================
Page                The page on which visits will be counted.
Count               The amount of visits to match.
Operator            Whether to match for more than, less than or equal to the
                    specified visit count.
==================  ==========================================================

``wagtail_personalisation.rules.VisitCountRule``


Query rule
----------

The query rule allows you to match a visitor based on the query included in
the url. It let's you define both the parameter and the value. It will look
something like this:

.. code-block:: bash

   example.com/?campaign=ourbestoffer

==================  ==========================================================
Option              Description
==================  ==========================================================
Parameter           The first part of the query ('campaign').
Value               The second part of the query ('ourbestoffer').
==================  ==========================================================

``wagtail_personalisation.rules.QueryRule``


Device rule
-----------

The device rule allows you to match visitors by the type of device they are
using. You can select any combination you want.

==================  ==========================================================
Option              Description
==================  ==========================================================
Mobile phone        Matches when the visitor uses a mobile phone.
Tablet              Matches when the visitor uses a tablet.
Desktop             Matches when the visitor uses a desktop.
==================  ==========================================================

``wagtail_personalisation.rules.DeviceRule``


User is logged in rule
----------------------

The user is logged in rule allows you to match visitors that are authenticated
and logged in to your app.

==================  ==========================================================
Option              Description
==================  ==========================================================
Is logged in        Whether the user is logged in or logged out.
==================  ==========================================================

``wagtail_personalisation.rules.UserIsLoggedInRule``


Origin country rule
-------------------

The origin country rule allows you to match visitors based on the origin
country of their request. This rule requires to have set up a way to detect
countries beforehand.

==================  ==========================================================
Option              Description
==================  ==========================================================
Country             What country user's request comes from.
==================  ==========================================================

You must have one of the following configurations set up in order to
make it work.

- Cloudflare IP Geolocation - ``cf-ipcountry`` HTTP header set with a value of
  the alpha-2 country format.
- CloudFront Geo-Targeting - ``cloudfront-viewer-country`` header set with a
  value of the alpha-2 country format.
- The last fallback is to use GeoIP2 module that is included with Django. This
  requires setting up an IP database beforehand, see the Django's
  `GeoIP2 instructions <https://docs.djangoproject.com/en/stable/ref/contrib/gis/geoip2/>`_
  for more information. It will use IP of the request, using HTTP header
  the ``x-forwarded-for`` HTTP header and ``REMOTE_ADDR`` server value as a
  fallback. If you want to use a custom logic when obtaining IP address, please
  set the ``WAGTAIL_PERSONALISATION_IP_FUNCTION`` setting to the function that takes a
  request as an argument, e.g.

  .. code-block:: python

     # settings.py

     WAGTAIL_PERSONALISATION_IP_FUNCTION = 'yourproject.utils.get_client_ip'


     # yourproject/utils.py

     def get_client_ip(request):
         return request['HTTP_CF_CONNECTING_IP']

``wagtail_personalisation.rules.OriginCountryRule``
