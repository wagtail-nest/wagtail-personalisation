from django.template import Library

from wagtail_personalisation.adapters import get_segment_adapter

register = Library()


@register.inclusion_tag('wagtail_personalisation/tags/datalayer.html', takes_context=True)
def render_datalayer(context):
    """Render the sessions active segments in a data layer script tag."""
    request = context.get('request')
    if request:
        segments = get_segment_adapter(request).get_all_segments()
        segment_names = [item['encoded_name'] for item in segments]

        return {
            'segments': segment_names
        }
