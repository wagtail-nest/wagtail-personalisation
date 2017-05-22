from django.template import Library

from personalisation.app_settings import segments_adapter

register = Library()


@register.inclusion_tag('personalisation/tags/datalayer.html')
def render_datalayer():
    """Render the sessions active segments in a data layer script tag."""
    segments = segments_adapter.get_all_segments()
    segment_names = [item['encoded_name'] for item in segments]

    return {
        'segments': segment_names
    }
