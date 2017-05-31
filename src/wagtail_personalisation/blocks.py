from __future__ import absolute_import, unicode_literals

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import Segment


def list_segment_choices():
    """Get a list of segment choices visible in the admin site when editing
    BasePersonalisedStructBlock and its derived classes."""
    yield (-1, _('Visible to everyone'))

    for pk, name in Segment.objects.values_list('pk', 'name'):
        yield pk, name


class BasePersonalisedStructBlock(blocks.StructBlock):
    """Base class for personalised struct blocks."""
    segment = blocks.ChoiceBlock(
        choices=list_segment_choices,
        required=False, label=_("Personalisation segment"),
        help_text=_("Only show this content block for users in this segment"))

    def __init__(self, *args, **kwargs):
        """Instantiate personalised struct block.

        The arguments are the same as for the blocks.StructBlock constructor and
        one addtional one.

        Keyword Arguments:
            render_fields: List with field names to be rendered or None to use
                the default block rendering. Please set to None if using block
                with template since then it's the template that takes care
                of what fields are rendered.
        """
        render_fields = kwargs.pop('render_fields',
                                   self._meta_class.render_fields)
        super(BasePersonalisedStructBlock, self).__init__(*args, **kwargs)

        # Check "render_fields" are either a list or None.
        if isinstance(render_fields, tuple):
            render_fields = list(render_fields)

        if render_fields is not None \
                and not isinstance(render_fields, list):
            raise ValueError('"render_fields" has to be a list or None.')
        elif isinstance(render_fields, list) \
                and not set(render_fields).issubset(self.child_blocks):
            raise ValueError('"render_fields" has to contain name(s) of the '
                             'specified blocks.')
        else:
            setattr(self.meta, 'render_fields', render_fields)

        # Template can be used only when "render_fields" is set to None.
        if self.meta.render_fields is not None \
                and getattr(self.meta, 'template', None):
            raise ValueError('"render_fields" has to be set to None when using '
                             'template.')


    def is_visible(self, value, request):
        """Check whether user should see the block based on their segments.

        :param value: The value from the block.
        :type value: dict
        :returns: True if user should see the block.
        :rtype: bool

        """
        if int(value['segment']) == -1:
            return True

        if value['segment']:
            for segment in get_segment_adapter(request).get_segments():
                if segment.id == int(value['segment']):
                    return True

        return False

    def render(self, value, context=None):
        """Only render this content block for users in this segment.

        :param value: The value from the block
        :type value: dict
        :param context: The context containing the request
        :type context: dict
        :returns: The provided block if matched, otherwise an empty string
        :rtype: blocks.StructBlock or empty str

        """
        if not self.is_visible(value, context['request']):
            return ""

        if self.meta.render_fields is None:
            return super(BasePersonalisedStructBlock, self).render(
                value, context)

        if isinstance(self.meta.render_fields, list):
            render_value = ''
            for field_name in self.meta.render_fields:
                if hasattr(value.bound_blocks[field_name], 'render_as_block'):
                    block_value = value.bound_blocks[field_name] \
                                         .render_as_block(context=context)
                else:
                    block_value = force_text(value[field_name])

                if block_value != 'None':
                    render_value += block_value

            return render_value

        raise RuntimeError('"render_fields" is neither "None" or "list" '
                           'during rendering.')

    class Meta:
        """
        Setting render field will  define which field gets rendered.
        Please use a name of the field. If none, it will render the whole block.
        """
        render_fields = None


class PersonalisedStructBlock(BasePersonalisedStructBlock):
    """Struct block that allows personalisation per block."""

    class Meta:
        label = _('Personalised Block')
        render_fields = None


class PersonalisedRichTextBlock(BasePersonalisedStructBlock):
    """Rich text block that allows personalisation."""
    rich_text = blocks.RichTextBlock(label=_('Rich Text'))

    class Meta:
        icon = blocks.RichTextBlock._meta_class.icon
        label = _('Personalised Rich Text')
        render_fields = ['rich_text']


class PersonalisedTextBlock(BasePersonalisedStructBlock):
    """Text block that allows personalisation."""
    text = blocks.TextBlock(label=_('Mutli-line Text'))

    class Meta:
        icon = blocks.TextBlock._meta_class.icon
        label = _('Personalised Multi-line Text')
        render_fields = ['text']


class PersonalisedCharBlock(BasePersonalisedStructBlock):
    """Char block that allows personalisation."""
    char = blocks.CharBlock(label=_('Text'))

    class Meta:
        icon = blocks.CharBlock._meta_class.icon
        label = _('Personalised Single-line Text')
        render_fields = ['char']


class PersonalisedImageChooserBlock(BasePersonalisedStructBlock):
    """Image chooser block that allows personalisation."""
    image = ImageChooserBlock(label=_('Image'))

    class Meta:
        icon = ImageChooserBlock._meta_class.icon
        label = _('Personalised Image')
        render_fields = ['image']

