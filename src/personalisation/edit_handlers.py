from django import forms
from django.forms import HiddenInput
from django.utils.safestring import mark_safe


class ReadOnlyWidget(forms.Select):
    """
    Render the original field as a hidden widget.
    And create a text display for the label
    """
    def __init__(self, text_display, *args, **kwargs):
        self.text_display = text_display
        self.initial_widget = HiddenInput()
        super(ReadOnlyWidget, self).__init__(*args, **kwargs)

    def render(self, *args, **kwargs):
        original_content = self.initial_widget.render(*args, **kwargs)

        return mark_safe("""<span class="hidden">%s</span>%s""" % (
            original_content, self.text_display))
