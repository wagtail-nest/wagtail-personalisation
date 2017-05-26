from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _
from wagtail_personalisation.models import Segment
from wagtail.wagtailcore import blocks


def list_segment_choices():
    for segment in Segment.objects.all():
        yield (segment.pk, segment.name)


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
        # TODO: move logic to its own class instead of getting it from the
        # session.
        user_segments = context['request'].session['segments']

        if value['segment']:
            for segment in user_segments:
                if segment['id'] == int(value['segment']):
                    return super(PersonalisedStructBlock, self).render(
                        value, context)

        return ""
