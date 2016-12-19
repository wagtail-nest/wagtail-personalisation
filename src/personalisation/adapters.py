import time

from personalisation.models import AbstractBaseRule, Segment

class BaseSegmentsAdapter(object):
    """Base adapter with required functions predefined"""
    def setup(self):
        return

    def get(self):
        return

    def add(self):
        return

    def refresh(self):
        return

    def check_segment_exists(self):
        return

    class Meta:
        abstract = True


class SessionSegmentsAdapter(BaseSegmentsAdapter):
    """Segments adapter that uses Django's SessionMiddleware to store segments"""
    # Setup
    def setup(self, request):
        self.request = request

        # Set up segments dictionary object in the session
        if 'segments' not in self.request.session:
            self.request.session['segments'] = []

    # Get segments
    def get(self):
        return self.request.session['segments']

    # Add segments
    def add(self, segment):
        def check_if_segmented(item):
            """Check if the user has been segmented"""
            for seg in self.request.session['segments']:
                if seg['encoded_name'] == item.encoded_name():
                    return True
            return False

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

        current_segments = [item for item in current_segments if
                            any(seg.pk for seg in persistent_segments) == item['id']]

        self.request.session['segments'] = current_segments

        segments = Segment.objects.all().filter(status='enabled')

        for segment in segments:
            rules = AbstractBaseRule.__subclasses__()
            segment_rules = []
            for rule in rules:
                queried_rules = rule.objects.filter(segment=segment)
                for result in queried_rules:
                    segment_rules.append(result)
            result = _test_rules(segment_rules, self.request)

            if result:
                self.add(segment)


        for seg in self.request.session['segments']:
            segment = Segment.objects.get(pk=seg['id'])
            segment.visit_count = segment.visit_count + 1
            segment.save()

    # Quick checking logic to see if a segment exists
    def check_segment_exists(self, segment):
        segments = self.request.session['segments']

        return any(item for item in self.request.session['segments'] if segment.pk == item.id)


def _test_rules(rules, request):
    """Test whether the user matches a segment's rules'"""
    if len(rules) > 0:
        for rule in rules:
            result = rule.test_user(request)

            if result is False:
                return False

        return True
    return False
