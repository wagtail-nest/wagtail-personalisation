from django.conf import settings
from django.db.models import F
from django.utils.module_loading import import_string

from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import AbstractBaseRule
from wagtail_personalisation.utils import create_segment_dictionary


class BaseSegmentsAdapter:
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
        if not rules:
            return False
        if match_any:
            return any(rule.test_user(request) for rule in rules)
        return all(rule.test_user(request) for rule in rules)

    class Meta:
        abstract = True


class SessionSegmentsAdapter(BaseSegmentsAdapter):
    """Segment adapter that uses Django's session backend."""

    def __init__(self, request):
        super(SessionSegmentsAdapter, self).__init__(request)
        self.request.session.setdefault('segments', [])
        self._segment_cache = None

    def _segments(self, ids=None):
        if not ids:
            ids = []
        segments = (
            Segment.objects
            .enabled()
            .filter(persistent=True)
            .filter(pk__in=ids)
        )
        return segments

    def get_segments(self, key="segments"):
        """Return the persistent segments stored in the request session.

        :param key: The key under which the segments are stored
        :type key: String
        :returns: The segments in the request session
        :rtype: list of wagtail_personalisation.models.Segment or empty list

        """
        if key == "segments" and self._segment_cache is not None:
            return self._segment_cache

        if key not in self.request.session:
            return []
        raw_segments = self.request.session[key]
        segment_ids = [segment['id'] for segment in raw_segments]

        segments = self._segments(ids=segment_ids)

        result = list(segments)
        if key == "segments":
            self._segment_cache = result
        return result

    def set_segments(self, segments, key="segments"):
        """Set the currently active segments

        :param segments: The segments to set for the current request
        :type segments: list of wagtail_personalisation.models.Segment
        :param key: The key under which to store the segments. Optional
        :type key: String

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

        self.request.session[key] = serialized_segments
        if key == "segments":
            self._segment_cache = cache_segments

    def get_segment_by_id(self, segment_id):
        """Find and return a single segment from the request session.

        :param segment_id: The primary key of the segment
        :type segment_id: int
        :returns: The matching segment
        :rtype: wagtail_personalisation.models.Segment or None

        """
        segments = self._segments(ids=[segment_id])
        if segments.exists():
            return segments.get()

    def add_page_visit(self, page):
        """Mark the page as visited by the user"""
        visit_count = self.request.session.setdefault('visit_count', [])
        page_visits = [visit for visit in visit_count if visit['id'] == page.pk]

        if page_visits:
            for page_visit in page_visits:
                page_visit['count'] += 1
                page_visit['path'] = page.url_path if page else self.request.path
            self.request.session.modified = True
        else:
            visit_count.append({
                'slug': page.slug,
                'id': page.pk,
                'path': page.url_path if page else self.request.path,
                'count': 1,
            })

    def get_visit_count(self, page=None):
        """Return the number of visits on the current request or given page"""
        path = page.url_path if page else self.request.path
        visit_count = self.request.session.setdefault('visit_count', [])
        for visit in visit_count:
            if visit['path'] == path:
                return visit['count']
        return 0

    def update_visit_count(self):
        """Update the visit count for all segments in the request session."""
        segments = self.request.session['segments']
        segment_pks = [s['id'] for s in segments]

        # Update counts
        (Segment.objects
            .enabled()
            .filter(pk__in=segment_pks)
            .update(visit_count=F('visit_count') + 1))

    def refresh(self):
        """Retrieve the request session segments and verify whether or not they
        still apply to the requesting visitor.

        """
        enabled_segments = Segment.objects.enabled()
        rule_models = AbstractBaseRule.get_descendant_models()

        current_segments = self.get_segments()
        excluded_segments = self.get_segments("excluded_segments")
        current_segments = list(
            set(current_segments) - set(excluded_segments)
        )

        # Run tests on all remaining enabled segments to verify applicability.
        additional_segments = []
        for segment in enabled_segments:
            if segment.is_static and segment.static_users.filter(id=self.request.user.id).exists():
                additional_segments.append(segment)
            elif any((
                segment.excluded_users.filter(id=self.request.user.id).exists(),
                segment in excluded_segments
            )):
                continue
            elif not segment.is_static or not segment.is_full:
                segment_rules = []
                for rule_model in rule_models:
                    segment_rules.extend(rule_model.objects.filter(segment=segment))

                result = self._test_rules(segment_rules, self.request,
                                          match_any=segment.match_any)

                if result and segment.randomise_into_segment():
                    if segment.is_static and not segment.is_full:
                        if self.request.user.is_authenticated:
                            segment.static_users.add(self.request.user)
                    additional_segments.append(segment)
                elif result:
                    if segment.is_static and self.request.user.is_authenticated:
                        segment.excluded_users.add(self.request.user)
                    else:
                        excluded_segments += [segment]

        self.set_segments(current_segments + additional_segments)
        self.set_segments(excluded_segments, "excluded_segments")
        self.update_visit_count()


SEGMENT_ADAPTER_CLASS = import_string(getattr(
    settings,
    'PERSONALISATION_SEGMENTS_ADAPTER',
    'wagtail_personalisation.adapters.SessionSegmentsAdapter'))


def get_segment_adapter(request):
    """Return the Segment Adapter for the given request"""
    if not hasattr(request, 'segment_adapter'):
        request.segment_adapter = SEGMENT_ADAPTER_CLASS(request)
    return request.segment_adapter
