from django import template
from django.template import TemplateSyntaxError
from django.template.base import FilterExpression, kwarg_re
from django.utils.safestring import mark_safe

from wagtail_personalisation.app_settings import segments_adapter
from wagtail_personalisation.models import Segment

register = template.Library()


def parse_tag(token, parser):
    """
    Generic template tag parser.

    Returns a three-tuple: (tag_name, args, kwargs)

    tag_name is a string, the name of the tag.

    args is a list of FilterExpressions, from all the arguments that didn't look like kwargs,
    in the order they occurred, including any that were mingled amongst kwargs.

    kwargs is a dictionary mapping kwarg names to FilterExpressions, for all the arguments that
    looked like kwargs, including any that were mingled amongst args.

    (At rendering time, a FilterExpression f can be evaluated by calling f.resolve(context).)
    """
    # Split the tag content into words, respecting quoted strings.
    bits = token.split_contents()

    # Pull out the tag name.
    tag_name = bits.pop(0)

    # Parse the rest of the args, and build FilterExpressions from them so that
    # we can evaluate them later.
    args = []
    kwargs = {}
    for bit in bits:
        # Is this a kwarg or an arg?
        match = kwarg_re.match(bit)
        kwarg_format = match and match.group(1)
        if kwarg_format:
            key, value = match.groups()
            kwargs[key] = FilterExpression(value, parser)
        else:
            args.append(FilterExpression(bit, parser))

    return (tag_name, args, kwargs)


def do_segment(parser, token):
    """Block that only shows content if user is in chosen segment.
    """
    # Parse the tag
    tag_name, _, kwargs = parse_tag(token, parser)

    # If no segment is provided this block will raise an error
    if set(kwargs.keys()) != {'name'}:
        usage = '{% {tag_name} name="segmentname" %} ... {% end{tag_name} %}'.format(tag_name=tag_name)
        raise TemplateSyntaxError("Usage: %s" % usage)

    nodelist = parser.parse(('endsegment',))
    parser.delete_first_token()

    return SegmentNode(nodelist, name=kwargs['name'])


register.tag('segment', do_segment)


class SegmentNode(template.Node):
    def __init__(self, nodelist, name):
        self.nodelist = nodelist
        self.name = name

    def render(self, context):
        # Check if segment exists
        name = self.name.resolve(context)
        segment = Segment.objects.filter(name=name).first()
        if not segment:
            return ""

        # Check if user has segment
        user_segment = segments_adapter.get_segment(segment_id=segment.pk)
        if not user_segment:
            return ""

        content = self.nodelist.render(context)
        content = mark_safe(content)

        return content
