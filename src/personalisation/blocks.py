from __future__ import absolute_import, unicode_literals

from wagtail.wagtailcore import blocks

from personalisation.models import Segment


def list_segment_choices():
    for s in Segment.objects.all():
        yield (s.pk, s.name)


class PersonalisedStructBlock(blocks.StructBlock):
    segment = blocks.ChoiceBlock(
        choices=list_segment_choices, 
        required=False, label=_("Personalisation segment"),
        help_text=_("Only show this content block for users in this segment"))

    def render(self, value, context=None):
        """Only render this content block for users in this segment"""
        # TODO: move logic to its own class instead of getting it from the session
        user_segments = context['request'].session['segments']

        if value['segment']:
            for segment in user_segments:
                if segment['id'] == int(value['segment']):
                    return super(PersonalisedStructBlock, self).render(value,
                        context)

        return ""
