from wagtail.wagtailcore import blocks
from personalisation.models import Segment

class PersonalisedStructBlock(blocks.StructBlock):

    if Segment.objects.count() > 0:
    	segment = blocks.ChoiceBlock(choices=[
            (segment.pk, "{} ({})".format(segment.name, segment.status) ) \
                for segment in Segment.objects.all()
        ], required=False, label="Personalisation segment",
        help_text="Only show this content block for users in this segment")

