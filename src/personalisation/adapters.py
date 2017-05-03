from __future__ import absolute_import, unicode_literals
import time

from django.db.models import F

from personalisation.models import Segment
from personalisation.rules import AbstractBaseRule


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

    def check_segment_exists(self):
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
            segdict = {
                "encoded_name": segment.encoded_name(),
                "id": segment.pk,
                "timestamp": int(time.time()),
                "persistent": segment.persistent,
            }
            self.request.session['segments'].append(segdict)

    def refresh(self):
        current_segments = self.request.session['segments']
        persistent_segments = Segment.objects.filter(persistent=True)

        new_segments = []

        for cseg in current_segments:
            for pseg in persistent_segments:
                if pseg.pk == cseg['id']:
                    new_segments.append(cseg)

        self.request.session['segments'] = new_segments

        segments = Segment.objects.filter(status='enabled')

        for segment in segments:
            rules = AbstractBaseRule.__subclasses__()
            segment_rules = []
            for rule in rules:
                segment_rules += rule.objects.filter(segment=segment)
            result = self._test_rules(segment_rules, self.request, match_any=segment.match_any)

            if result:
                self.add(segment)

        for seg in self.request.session['segments']:
            segment = Segment.objects.get(pk=seg['id'])
            segment.visit_count = F('visit_count') + 1
            segment.save()

    def check_segment_exists(self, segment):
        segments = self.request.session['segments']

        return any(item for item in segments if segment.pk == item.id)

