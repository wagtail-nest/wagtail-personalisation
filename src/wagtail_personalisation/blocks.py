from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailcore import blocks

from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import Segment


def list_segment_choices():
    for pk, name in Segment.objects.values_list('pk', 'name'):
        yield pk, name


class PersonalisedStructBlock(blocks.StructBlock):
    """Struct block that allows personalisation per block."""

    segment = blocks.ChoiceBlock(
        choices=list_segment_choices,
        required=False, label=_("Personalisation segment"),
        help_text=_("Only show this content block for users in this segment"))

    def render(self, value, context=None):
        """Only render this content block for users in this segment.

        :param value: The value from the block
        :type value: dict
        :param context: The context containing the request
        :type context: dict
        :returns: The provided block if matched, otherwise an empty string
        :rtype: blocks.StructBlock or empty str

        """
        request = context['request']
        adapter = get_segment_adapter(request)
        user_segments = adapter.get_segments()

        if value['segment']:
            for segment in user_segments:
                if segment.id == int(value['segment']):
                    return super(PersonalisedStructBlock, self).render(
                        value, context)

        return ""
