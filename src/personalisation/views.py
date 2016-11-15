from __future__ import absolute_import, unicode_literals

from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView
from wagtail.contrib.modeladmin.views import CreateView
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, ObjectList, PageChooserPanel, TabbedInterface)

from personalisation.forms import (
    PersonalisationForm, ReferralRuleForm, SegmentForm, TimeRuleForm,
    VisitCountRuleForm)
from personalisation.models import PersonalisablePage, Segment


def overview(request):
    """Display segments overview. Dummy function"""
    return render(request, 'wagtailadmin/segment.html')


def enable(request, segment_id):
    """Enable the selected segment"""
    segment = get_object_or_404(Segment, pk=segment_id)
    segment.status = 'enabled'
    segment.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def disable(request, segment_id):
    """Disable the selected segment"""
    segment = get_object_or_404(Segment, pk=segment_id)
    segment.status = 'disabled'
    segment.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# TODO: Make these requestable from an existing page (the create page)
# This code might become obsolete.


def time_rule_embed(request):
    """Show the content of the time rule modal."""
    return render(request, 'wagtailadmin/embeds/time_rule.html', {
        'form': TimeRuleForm,
    })


def referral_rule_embed(request):
    """Show the content of the referral rule modal."""
    return render(request, 'wagtailadmin/embeds/referral_rule.html', {
        'form': ReferralRuleForm,
    })


def visit_count_rule_embed(request):
    """Show the content of the visit count rule modal."""
    return render(request, 'wagtailadmin/embeds/visit_count_rule.html', {
        'form': VisitCountRuleForm,
    })


class CreateSegmentView(CreateView):
    page_title = _("Add segment")
    form_class = SegmentForm
    template_name = 'modeladmin/personalisation/segment/create.html'
    header_icon = 'folder-open-1'


class AddVariation(FormView):
    form_class = PersonalisationForm

    add_variation_panels = [
        FieldPanel('copy_from_canonical'),
        PageChooserPanel('parent_page'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(add_variation_panels, heading='Variation',
                   base_form_class=PersonalisationForm)
    ])

    def dispatch(self, request, page_pk, segment_name, *args, **kwargs):
        self.page = get_object_or_404(PersonalisablePage, pk=page_pk)
        self.segment = get_object_or_404(Segment, name=segment_name)

        super(AddVariation, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        form_kwargs = super(AddVariation, self).get_form_kwargs(*args, **kwargs)
        form_kwargs.update({
            'page': self.page,
            'segment': self.segment,
        })
        return form_kwargs

    def form_valid(self, form):
        parent = form.cleaned_data['parent_page']
        copy_from_canonical = form.cleaned_data['copy_from_canonical']

        new_page = self.page.create_variation(
            self.segment, copy_fields=copy_from_canonical, parent=parent)

        return redirect(
            'wagtailadmin_pages:edit', new_page.id
        )

    def get_context_data(self, *args, **kwargs):
        context = super(AddVariation, self).get_context_data(*args, **kwargs)
        edit_handler = self.edit_handler.bind_to_model(self.page)

        context.update({
            'page': self.page,
            'segment': self.segment,
            'content_type': self.page.content_type,
            'parent_page': self.page.get_parent(),
            'edit_handler': edit_handler(self.page, context['form']),
        })

        return context
