from __future__ import absolute_import, unicode_literals

from django.conf import settings
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

    def get_segments(self):
        """Return the segments stored in the adapter storage."""

    def get_segment_by_id(self):
        """Return a single segment stored in the adapter storage."""

    def add(self):
        """Add a new segment to the adapter storage."""

    def refresh(self):
        """Refresh the segments stored in the adapter storage."""

    def _test_rules(self, rules, match_any=False):
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
        if not rules:
            return False

        if not hasattr(self.request, 'matched_rules'):
            self.request.matched_rules = []

        results = []
        for rule in rules:
            validation = rule.test_user(self.request)
            if validation:
                self.request.matched_rules.append(rule.unique_encoded_name)
            results.append(validation)

        if match_any:
            return any(results)
        return all(results)

    class Meta:
        abstract = True


class SessionSegmentsAdapter(BaseSegmentsAdapter):
    """Segment adapter that uses Django's session backend."""

    def __init__(self, request):
        super(SessionSegmentsAdapter, self).__init__(request)
        self.request.session.setdefault('segments', [])
        self._segment_cache = None

    def get_segments(self):
        """Return the persistent segments stored in the request session.

        :returns: The segments in the request session
        :rtype: list of wagtail_personalisation.models.Segment or empty list

        """
        if self._segment_cache is not None:
            return self._segment_cache

        raw_segments = self.request.session['segments']
        segment_ids = [segment['id'] for segment in raw_segments]

        segments = (
            Segment.objects
            .enabled()
            .filter(persistent=True)
            .in_bulk(segment_ids))

        retval = [segments[pk] for pk in segment_ids if pk in segments]
        self._segment_cache = retval
        return retval

    def set_segments(self, segments):
        """Set the currently active segments

        :param segments: The segments to set for the current request
        :type segments: list of wagtail_personalisation.models.Segment

        """
        cache_segments = []
        serialized_segments = []
        segment_ids = set()
        for segment in segments:
            serialized = create_segment_dictionary(segment)
            if serialized['id'] in segment_ids:
                continue

            cache_segments.append(segment)
            serialized_segments.append(serialized)
            segment_ids.add(segment.pk)

        self.request.session['segments'] = serialized_segments
        self._segment_cache = cache_segments

    def get_segment_by_id(self, segment_id):
        """Find and return a single segment from the request session.

        :param segment_id: The primary key of the segment
        :type segment_id: int
        :returns: The matching segment
        :rtype: wagtail_personalisation.models.Segment or None

        """
        for segment in self.get_segments():
            if segment.pk == segment_id:
                return segment

    def add_page_visit(self, page):
        """Mark the page as visited by the user"""
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

    def refresh(self):
        """Retrieve the request session segments and verify whether or not they
        still apply to the requesting visitor.

        """
        enabled_segments = Segment.objects.enabled()
        rule_models = AbstractBaseRule.get_descendant_models()

        current_segments = self.get_segments()

        # Run tests on all remaining enabled segments to verify applicability.
        additional_segments = []
        for segment in enabled_segments:
            segment_rules = []
            for rule_model in rule_models:
                segment_rules.extend(rule_model.objects.filter(segment=segment))

            result = self._test_rules(
                segment_rules, match_any=segment.match_any)

            if result:
                additional_segments.append(segment)

        self.set_segments(current_segments + additional_segments)


SEGMENT_ADAPTER_CLASS = import_string(getattr(
    settings,
    'PERSONALISATION_SEGMENTS_ADAPTER',
    'wagtail_personalisation.adapters.SessionSegmentsAdapter'))


def get_segment_adapter(request):
    """Return the Segment Adapter for the given request"""
    if not hasattr(request, 'segment_adapter'):
        request.segment_adapter = SEGMENT_ADAPTER_CLASS(request)
    return request.segment_adapter
