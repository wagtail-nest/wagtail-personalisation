from __future__ import absolute_import, unicode_literals

from django.db.models import F

from personalisation.models import Segment
from personalisation.rules import AbstractBaseRule
from personalisation.utils import create_segment_dictionary


class BaseSegmentsAdapter(object):
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
    """
    Segment adapter that uses Django's session backend.
    """
    def setup(self, request):
        self.request = request

        self.request.session.setdefault('segments', [])

    def get_all_segments(self):
        return self.request.session['segments']

    def get_segment(self, segment_id):
        return next(item for item in self.request.session['segments'] if item.id == segment_id)

    def add(self, segment):
        def check_if_segmented(item):
            """Check if the user has been segmented"""
            return any(seg['encoded_name'] == item.encoded_name() for seg in self.request.session['segments'])

        if not check_if_segmented(segment):
            segdict = create_segment_dictionary(segment)
            self.request.session['segments'].append(segdict)

    def refresh(self):
        def update_visit_count(self):
            for seg in self.request.session['segments']:
                segment = Segment.objects.get(pk=seg['id'])
                segment.visit_count = F('visit_count') + 1
                segment.save()

        segments = Segment.objects.filter(status='enabled')
        persistent_segments = segments.filter(persistent=True)
        session_segments = self.request.session['segments']
        rules = AbstractBaseRule.__subclasses__()

        new_segments = []

        for session_segment in session_segments:
            for persistent_segment in persistent_segments:
                if persistent_segment.pk == session_segment['id']:
                    new_segments.append(session_segment)

        for segment in segments:
            segment_rules = []
            for rule in rules:
                segment_rules += rule.objects.filter(segment=segment)
            result = self._test_rules(segment_rules, self.request, match_any=segment.match_any)

            if result:
                segdict = create_segment_dictionary(segment)
                if not any(seg['id'] == segdict['id'] for seg in new_segments):
                    new_segments.append(segdict)

        self.request.session['segments'] = new_segments

        update_visit_count(self)
