from __future__ import absolute_import, unicode_literals

from django.db.models import F

from personalisation.models import Segment
from personalisation.rules import AbstractBaseRule
from personalisation.utils import create_segment_dictionary


class BaseSegmentsAdapter(object):
    """Base segments adapter."""

    def setup(self):
        return None

    def get_all_segments(self):
        return None

    def get_segment(self):
        return None

    def add(self):
        return None

    def refresh(self):
        return None

    def _test_rules(self, rules, request, match_any=False):
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

    def setup(self, request):
        """Prepare the request session for segment storage.
        
        :param request: The http request
        :type request: django.http.HttpRequest
        
        """
        self.request = request

        self.request.session.setdefault('segments', [])

    def get_all_segments(self):
        """Return the segments stored in the request session.
        
        :returns: The segments in the request session
        :rtype: list of personalisation.models.Segment or empty list
        
        """
        return self.request.session['segments']

    def get_segment(self, segment_id):
        """Find and return a single segment from the request session.
        
        :param segment_id: The primary key of the segment
        :type segment_id: int
        :returns: The matching segment
        :rtype: personalisation.models.Segment or None
        
        """
        return next(item for item in self.request.session['segments'] if item.id == segment_id)

    def add(self, segment):
        """Add a segment to the request session.
        
        :param segment: The segment to add to the request session
        :type segment: personalisation.models.Segment
        
        """

        def check_if_segmented(item):
            """Check if the user has been segmented.
            
            :param item: The segment to check for
            :type item: personalisation.models.Segment
            :returns: Whether the segment is in the request session
            :rtype: bool
            
            """
            return any(seg['encoded_name'] == item.encoded_name() for seg in self.request.session['segments'])

        if not check_if_segmented(segment):
            segdict = create_segment_dictionary(segment)
            self.request.session['segments'].append(segdict)

    def update_visit_count(self):
        """Update the visit count for all segments in the request session."""
        segments = self.request.sessions['segments']
        for seg in segments:
            try:
                segment = Segment.objects.get(pk=seg['id'])
                segment.visit_count = F('visit_count') + 1
                segment.save()

            except Segment.DoesNotExist:
                # The segment no longer exists.
                # Remove it from the request session.
                self.request.session['segments'][:] = [item for item in segments if item.get('id') != seg['id']]

    def refresh(self):
        """Retrieve the request session segments and verify whether or not they
        still apply to the requesting visitor.
        
        """
        enabled_segments = Segment.objects.filter(status='enabled')
        persistent_segments = enabled_segments.filter(persistent=True)
        session_segments = self.request.session['segments']
        rules = AbstractBaseRule.__subclasses__()

        new_segments = []

        # Re-apply all persistent segments, as long as they are still enabled.
        for session_segment in session_segments:
            for persistent_segment in persistent_segments:
                if persistent_segment.pk == session_segment['id']:
                    new_segments.append(session_segment)

        # Run tests on all remaining enabled segments to verify applicability.
        for segment in enabled_segments:
            segment_rules = []
            for rule in rules:
                segment_rules += rule.objects.filter(segment=segment)
            result = self._test_rules(segment_rules, self.request, match_any=segment.match_any)

            if result:
                segdict = create_segment_dictionary(segment)
                if not any(seg['id'] == segdict['id'] for seg in new_segments):
                    new_segments.append(segdict)

        self.request.session['segments'] = new_segments

        self.update_visit_count()
