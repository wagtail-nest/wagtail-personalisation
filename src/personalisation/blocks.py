from wagtail.wagtailcore import blocks
from personalisation.models import Segment

class PersonalisedStructBlock(blocks.StructBlock):

    segment = blocks.ChoiceBlock(choices=[
        (segment.pk, "{} ({})".format(segment.name, segment.status) ) \
            for segment in Segment.objects.all()
        ], required=False, label="Personalisation segment",
        help_text="Only show this content block for users in this segment")


    def render(self, value, context=None):
        """Only render block when the user is in the segment the block is
        meant for"""

        user_segments = context['request'].session['segments']

        if value['segment']:
            for segment in user_segments:
                if segment['id'] == int(value['segment']):
                    return super(PersonalisedStructBlock, self).render(value,
                        context)

        return ""
