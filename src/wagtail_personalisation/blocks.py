from django.utils.translation import gettext_lazy as _
from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail import blocks
else:
    from wagtail.core import blocks

from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import Segment


def list_segment_choices():
    yield -1, ("Show to everyone")
    for pk, name in Segment.objects.values_list("pk", "name"):
        yield pk, name


class PersonalisedStructBlock(blocks.StructBlock):
    """Struct block that allows personalisation per block."""

    segment = blocks.ChoiceBlock(
        choices=list_segment_choices,
        required=False,
        label=_("Personalisation segment"),
        help_text=_("Only show this content block for users in this segment"),
    )

    def render(self, value, context=None):
        """Only render this content block for users in this segment.

        :param value: The value from the block
        :type value: dict
        :param context: The context containing the request
        :type context: dict
        :returns: The provided block if matched, otherwise an empty string
        :rtype: blocks.StructBlock or empty str

        """
        request = context["request"]
        adapter = get_segment_adapter(request)
        user_segments = adapter.get_segments()

        try:
            segment_id = int(value["segment"])
        except (ValueError, TypeError):
            return ""

        if segment_id > 0:
            for segment in user_segments:
                if segment.id == segment_id:
                    return super(PersonalisedStructBlock, self).render(value, context)

        if segment_id == -1:
            return super(PersonalisedStructBlock, self).render(value, context)

        return ""
