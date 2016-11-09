from personalisation.models import AbstractBaseRule, Segment


class SegmentMiddleware(object):
    """Middleware for testing and putting a user in a segment"""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        segments = Segment.objects.all().filter(status="enabled")

        chosen_segments = []

        for segment in segments:
            rules = AbstractBaseRule.objects.filter(segment=segment).select_subclasses()
            result = self.test_rules(rules, request)

            if result:
                self.add_segment_to_user(segment, request)

        response = self.get_response(request)

        if not request.session.get('segments'):
            request.session['segments'] = []

        print(request.session['segments'])

        return response

    def test_rules(self, rules, request):
        for rule in rules:
            result = rule.test_user(request)

            if result is False:
                return False

        return True

    def add_segment_to_user(self, segment, request):
        if 'segments' not in request.session:
            request.session['segments'] = []

        if segment not in request.session['segments']:
            request.session['segments'].append(segment.encoded_name())

