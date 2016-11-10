import time
import logging

logger = logging.getLogger()

from personalisation.models import AbstractBaseRule, Segment


class SegmentMiddleware(object):
    """Middleware for testing and putting a user in a segment"""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/django-admin/'):
            return self.get_response(request)

        if 'visit_count' not in request.session:
            request.session['visit_count'] = []

        if 'segments' not in request.session:
            request.session['segments'] = []

        segments = Segment.objects.all().filter(status='enabled')

        for segment in segments:
            rules = AbstractBaseRule.objects.filter(segment=segment)
            result = self.test_rules(rules, request)

            if result:
                self.add_segment_to_user(segment, request)

        response = self.get_response(request)

        logger.info("User has been added to the following segments: {}".format(request.session['segments']))
        return response

    def test_rules(self, rules, request):
        """Test wether the user matches a segment's rules'"""
        if len(rules) > 0:
            for rule in rules:
                result = rule.test_user(request)

                # Debug
                if result and rule.__class__.__name__ == "TimeRule":
                    print("User segmented. Time between {} and {}.".format(
                        rule.start_time,
                        rule.end_time))
                if result and rule.__class__.__name__ == "ReferralRule":
                    print("User segmented. Referral matches {}.".format(rule.regex_string))
                if result and rule.__class__.__name__ == "VisitCountRule":
                    print("User segmented. Visited {} {} {} times.".format(
                        rule.counted_page,
                        rule.operator,
                        rule.count))

                if result is False:
                    return False

            return True
        return False

    def add_segment_to_user(self, segment, request):
        """Save the segment in the user session"""
        def check_if_segmented(segment):
            """Check if the user has been segmented"""
            for seg in request.session['segments']:
                if seg['encoded_name'] == segment.encoded_name():
                    return True
            return False

        if not check_if_segmented(segment):
            segdict = {
                "encoded_name": segment.encoded_name(),
                "id": segment.pk,
                "timestamp": int(time.time()),
            }
            request.session['segments'].append(segdict)
