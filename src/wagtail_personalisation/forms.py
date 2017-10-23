from django.core.exceptions import ValidationError
from wagtail.wagtailadmin.forms import WagtailAdminModelForm


class SegmentAdminForm(WagtailAdminModelForm):
    def clean(self):
        cleaned_data = super(SegmentAdminForm, self).clean()

        rules = [form for formset in self.formsets.values() for form in formset if form not in formset.deleted_forms]
        consistent = rules and all(rule.instance.static for rule in rules)

        from .models import Segment
        if cleaned_data.get('type') == Segment.TYPE_STATIC and not cleaned_data.get('count') and not consistent:
            raise ValidationError({
                'count': ('Static segments with non-static compatible rules must include a count.'),
            })

        return cleaned_data
