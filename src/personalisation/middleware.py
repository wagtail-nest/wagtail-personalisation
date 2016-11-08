from personalisation.models import AbstractBaseRule, Segment


class SegmentMiddleware(object):
    """Middleware for testing and putting a user in a segment"""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        segments = Segment.objects.all().filter(status="live")

        chosen_segments = []

        for segment in segments:
            rules = AbstractBaseRule.objects.filter(segment=segment).select_subclasses()
            result = self.test_rules(rules, request)

            if result:
                chosen_segments.append(segment.encoded_name())

        request.session['segments'] = chosen_segments
        response = self.get_response(request)

        print(request.session['segments'])

        return response


    def test_rules(self, rules, request):
        for rule in rules:
            result = rule.test_user(request)

            if result is False:
                return False

        return True
