from personalisation.models import TimeRule

class SegmentMiddleware(object):
    """Middleware for testing and putting a user in a segment"""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        time_rules = TimeRule.objects.all()

        result = False

        for rule in time_rules:
            result = rule.test_user()

        request.session['segmented'] = result
        response = self.get_response(request)

        print(request.session['segmented'])

        return response
