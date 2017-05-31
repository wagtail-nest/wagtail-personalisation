from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db.models import F
from django.utils.module_loading import import_string

from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import AbstractBaseRule
from wagtail_personalisation.utils import create_segment_dictionary


class BaseSegmentsAdapter(object):
    """Base segments adapter."""

    def __init__(self, request):
        """Prepare the request session for segment storage.

        :param request: The http request
        :type request: django.http.HttpRequest

        """
        self.request = request

    def setup(self):
        """Prepare the adapter for segment storage."""
        return None

    def get_all_segments(self):
        """Return the segments stored in the adapter storage."""
        return None

    def get_segment(self):
        """Return a single segment stored in the adapter storage."""
        return None

    def add(self):
        """Add a new segment to the adapter storage."""
        return None

    def refresh(self):
        """Refresh the segments stored in the adapter storage."""
        return None

    def _test_rules(self, rules, request, match_any=False):
        """Tests the provided rules to see if the request still belongs
        to a segment.

        :param rules: The rules to test for
        :type rules: list of wagtail_personalisation.rules
        :param request: The http request
        :type request: django.http.HttpRequest
        :param match_any: Whether all rules need to match, or any
        :type match_any: bool
        :returns: A boolean indicating the segment matches the request
        :rtype: bool

        """
        if len(rules) > 0:
            for rule in rules:
                result = rule.test_user(request)
                if match_any:
                    if result is True:
                        return result

                elif result is False:
                    return False
            if not match_any:
                return True
        return False

    class Meta:
        abstract = True


class SessionSegmentsAdapter(BaseSegmentsAdapter):
    """Segment adapter that uses Django's session backend."""

    def __init__(self, request):
        super(SessionSegmentsAdapter, self).__init__(request)
        self.request.session.setdefault('segments', [])

    def get_all_segments(self):
        """Return the segments stored in the request session.

        :returns: The segments in the request session
        :rtype: list of wagtail_personalisation.models.Segment or empty list

        """
        return self.request.session['segments']

    def get_segment(self, segment_id):
        """Find and return a single segment from the request session.

        :param segment_id: The primary key of the segment
        :type segment_id: int
        :returns: The matching segment
        :rtype: wagtail_personalisation.models.Segment or None

        """
        return next(item for item in self.request.session['segments']
                    if item.id == segment_id)

    def add(self, segment):
        """Add a segment to the request session.

        :param segment: The segment to add to the request session
        :type segment: wagtail_personalisation.models.Segment

        """

        def check_if_segmented(item):
            """Check if the user has been segmented.

            :param item: The segment to check for
            :type item: wagtail_personalisation.models.Segment
            :returns: Whether the segment is in the request session
            :rtype: bool

            """
            return any(seg['encoded_name'] == item.encoded_name()
                       for seg in self.request.session['segments'])

        if not check_if_segmented(segment):
            segdict = create_segment_dictionary(segment)
            self.request.session['segments'].append(segdict)

    def add_page_visit(self, page):
        """Mar kthe page as visited by the user"""
        visit_count = self.request.session.setdefault('visit_count', [])
        page_visits = [visit for visit in visit_count if visit['id'] == page.pk]

        if page_visits:
            for page_visit in page_visits:
                page_visit['count'] += 1
            self.request.session.modified = True
        else:
            visit_count.append({
                'slug': page.slug,
                'id': page.pk,
                'path': self.request.path,
                'count': 1,
            })

    def get_visit_count(self, page=None):
        """Return the number of visits on the current request or given page"""
        path = page.path if page else self.request.path
        visit_count = self.request.session.setdefault('visit_count', [])
        for visit in visit_count:
            if visit['path'] == path:
                return visit['count']
        return 0

    def update_visit_count(self):
        """Update the visit count for all segments in the request session."""
        segments = self.request.session['segments']
        for seg in segments:
            try:
                segment = Segment.objects.get(pk=seg['id'])
                segment.visit_count = F('visit_count') + 1
                segment.save()

            except Segment.DoesNotExist:
                # The segment no longer exists.
                # Remove it from the request session.
                self.request.session['segments'][:] = [
                    item for item in segments if item.get('id') != seg['id']]

    def refresh(self):
        """Retrieve the request session segments and verify whether or not they
        still apply to the requesting visitor.

        """
        enabled_segments = Segment.objects.filter(status='enabled')
        persistent_segments = enabled_segments.filter(persistent=True)
        session_segments = self.request.session['segments']
        rules = AbstractBaseRule.__subclasses__()

        # Create a list to store the new request session segments and
        # re-apply all persistent segments (if they are still enabled).
        new_segments = [segment for segment in session_segments
                        if persistent_segments.filter(id=segment['id']).exists()]

        # Run tests on all remaining enabled segments to verify applicability.
        for segment in enabled_segments:
            segment_rules = []
            for rule in rules:
                segment_rules += rule.objects.filter(segment=segment)
            result = self._test_rules(segment_rules, self.request,
                                      match_any=segment.match_any)

            if result:
                segdict = create_segment_dictionary(segment)
                if not any(seg['id'] == segdict['id'] for seg in new_segments):
                    new_segments.append(segdict)

        self.request.session['segments'] = new_segments

        self.update_visit_count()


SEGMENT_ADAPTER_CLASS = import_string(getattr(
    settings,
    'PERSONALISATION_SEGMENTS_ADAPTER',
    'wagtail_personalisation.adapters.SessionSegmentsAdapter'))


def get_segment_adapter(request):
    """Return the Segment Adapter for the given request"""
    try:
        return request.segment_adapter
    except AttributeError:
        request.segment_adapter = SEGMENT_ADAPTER_CLASS(request)
        return request.segment_adapter
