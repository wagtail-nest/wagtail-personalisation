from personalisation.models import Segment, TimeRule

class SegmentMiddleware(object):
    """Middleware for testing and putting a user in a segment"""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        segments = Segment.objects.all().filter(status="live")

        chosen_segments = []

        for segment in segments:
            result = False
            rules = TimeRule.objects.all().filter(segment=segment)
            for rule in rules:
                result = rule.test_user()
            if result:
                chosen_segments.append(segment.encoded_name())

        request.session['segments'] = chosen_segments
        response = self.get_response(request)

        print(request.session['segments'])

        return response
