from django.template import Library

from personalisation.app_settings import segments_adapter

register = Library()


@register.inclusion_tag('personalisation/tags/datalayer.html')
def render_datalayer():
    segments = segments_adapter.get_all_segments()
    segment_names = [item.name for item in segments]

    return {
        'segments': segment_names
    }
