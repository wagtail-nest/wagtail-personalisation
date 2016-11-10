from personalisation.models import AbstractBaseRule, Segment


class SegmentMiddleware(object):
    """Middleware for testing and putting a user in a segment"""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/django-admin/'):
            return self.get_response(request)

        if 'segments' not in request.session:
            request.session['segments'] = []
            request.session['visit_count'] = 1

        segments = Segment.objects.all().filter(status='enabled')

        chosen_segments = []

        for segment in segments:
            rules = AbstractBaseRule.objects.filter(segment=segment)
            result = self.test_rules(rules, request)

            print(result)

            if result:
                self.add_segment_to_user(segment, request)

        response = self.get_response(request)

        print(request.session['segments'])
        return response

    def test_rules(self, rules, request):
        """Test wether the user matches a segment's rules'"""
        if len(rules) > 0:
            for rule in rules:
                result = rule.test_user(request)

                if result is False:
                    return False

            return True
        return False

    def add_segment_to_user(self, segment, request):
        """Register the request to the Segment model as visit
        and save the segment in the user session"""
        segment.visit_count = segment.visit_count + 1
        segment.save()

        if segment.encoded_name() not in request.session['segments']:
            request.session['segments'].append(segment.encoded_name())
