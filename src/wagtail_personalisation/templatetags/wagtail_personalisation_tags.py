from django import template
from django.template import TemplateSyntaxError
from django.utils.safestring import mark_safe

from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import Segment
from wagtail_personalisation.utils import parse_tag

register = template.Library()


def do_segment(parser, token):
    """Block that only shows content if user is in chosen segment."""
    # Parse the tag
    tag_name, _, kwargs = parse_tag(token, parser)

    # If no segment is provided this block will raise an error
    if set(kwargs.keys()) != {"name"}:
        usage = '{% segment name="segmentname" %} ... {% endsegment %}'
        raise TemplateSyntaxError("Usage: %s" % usage)

    nodelist = parser.parse(("endsegment",))
    parser.delete_first_token()

    return SegmentNode(nodelist, name=kwargs["name"])


register.tag("segment", do_segment)


class SegmentNode(template.Node):
    """Node that only returns contents if user is in the segment.

    This node checks if the chosen segment exists and if the
    user has been segmented in the chosen segment.
    If not it will return nothing

    """

    def __init__(self, nodelist, name):
        self.nodelist = nodelist
        self.name = name

    def render(self, context):
        # Check if segment exists
        name = self.name.resolve(context)
        segment = Segment.objects.enabled().filter(name=name).first()
        if not segment:
            return ""

        # Check if user has segment
        adapter = get_segment_adapter(context["request"])
        user_segment = adapter.get_segment_by_id(segment_id=segment.pk)
        if not user_segment:
            return ""

        content = self.nodelist.render(context)
        content = mark_safe(content)
        return content
