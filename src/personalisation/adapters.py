from personalisation.models import Segment

class BaseSegmentsAdapter(object):
    """Base adapter with required functions predefined"""
    def __init__(self):
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
    def __init__(self, request):
        self.request = request

        # Set up segments dictionary object in the session
        if 'segments' not in self.request.session:
            self.request.session['segments'] = []

    # Get segments
    def get(self):
        return self.request.session['segments']

    # Add segments
    def add(self, segment):
        self.request.session['segments'].append(segment)

    def refresh(self):
        current_segments = self.request.session['segments']
        persistent_segments = Segment.objects.filter(persistent=True)

        current_segments = [item for item in current_segments if
                            any(seg.pk for seg in persistent_segments) == item['id']]

        self.request.session['segments'] = current_segments

    # Quick checking logic to see if a segment exists
    def check_segment_exists(self, segment):
        segments = self.request.session['segments']

        return any(item for item in self.request.session['segments'] if segment.pk == item.id)
