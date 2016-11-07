class SegmentMiddleware(object):
    """Middleware for testing and putting a user in a segment"""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        request.session['segmented'] = True
        response = self.get_response(request)

        print(request.session['segmented'])

        return response
