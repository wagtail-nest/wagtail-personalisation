from __future__ import absolute_import, unicode_literals

import re
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from polymorphic.models import PolymorphicModel
from wagtail.utils.decorators import cached_classmethod
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, FieldRowPanel,
                                                InlinePanel, MultiFieldPanel,
                                                ObjectList, PageChooserPanel,
                                                TabbedInterface)
from wagtail.wagtailadmin.forms import WagtailAdminPageForm
from wagtail.wagtailcore.models import Page


@python_2_unicode_compatible
class AbstractBaseRule(PolymorphicModel):
    """Base for creating rules to segment users with"""
    segment = ParentalKey(
        'Segment',
        # TODO: Make the related names accesible to wagtail admin
        # for inlining them.
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss"
    )

    def test_user(self, request):
        """Test if the user matches this rule"""
        return True

    def __str__(self):
        return "Segmentation rule"


@python_2_unicode_compatible
class TimeRule(AbstractBaseRule):
    """Time rule to segment users based on a start and end time"""
    start_time = models.TimeField(_("Starting time"))
    end_time = models.TimeField(_("Ending time"))

    panels = [
        FieldRowPanel([
            FieldPanel('start_time'),
            FieldPanel('end_time'),
        ]),
    ]

    def __init__(self, *args, **kwargs):
        super(TimeRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        current_time = self.get_current_time()
        starting_time = self.start_time
        ending_time = self.end_time

        return starting_time <= current_time <= ending_time

    def get_current_time(self):
        """Mockable function for testing purposes"""
        return datetime.now().time()

    def __str__(self):
        return '{} - {}'.format(self.start_time, self.end_time)


@python_2_unicode_compatible
class ReferralRule(AbstractBaseRule):
    """Referral rule to segment users based on a regex test"""
    regex_string = models.TextField(_("Regex string to match the referer with"))

    panels = [
        FieldPanel('regex_string'),
    ]

    def __init__(self, *args, **kwargs):
        super(ReferralRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        pattern = re.compile(self.regex_string)

        if 'HTTP_REFERER' in request.META:
            referer = request.META['HTTP_REFERER']
            if pattern.search(referer):
                return True
        return False

    def __str__(self):
        return '{}'.format(self.regex_string)


@python_2_unicode_compatible
class VisitCountRule(AbstractBaseRule):
    """Visit count rule to segment users based on amount of visits"""
    OPERATOR_CHOICES = (
        ('more_than', 'More than'),
        ('less_than', 'Less than'),
        ('equal_to', 'Equal to'),
    )
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, default="ht")
    count = models.PositiveSmallIntegerField(default=0, null=True)
    counted_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
    )

    panels = [
        PageChooserPanel('counted_page'),
        FieldRowPanel([
            FieldPanel('operator'),
            FieldPanel('count'),
        ]),
    ]

    def __init__(self, *args, **kwargs):
        super(VisitCountRule, self).__init__(*args, **kwargs)

    def test_user(self, request):
        operator = self.operator
        segment_count = self.count

        # TODO: Figure out a way to have a correct count before the middleware
        # initiates the test function

        def get_visit_count(request):
            """Search through the sessions to get the page visit count
            corresponding to the request."""
            for page in request.session['visit_count']:
                if page['path'] == request.path:
                    return page['count']

        visit_count = get_visit_count(request)

        if visit_count and operator == "more_than":
            if visit_count > segment_count:
                return True
        elif visit_count and operator == "less_than":
            if visit_count < segment_count:
                return True
        elif visit_count and operator == "equal_to":
            if visit_count == segment_count:
                return True
        return False

    def __str__(self):
        operator_display = self.get_operator_display()
        return '{} {}'.format(operator_display, self.count)


@python_2_unicode_compatible
class Segment(ClusterableModel):
    """Model for a new segment"""
    name = models.CharField(max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    enable_date = models.DateTimeField(null=True, editable=False)
    disable_date = models.DateTimeField(null=True, editable=False)
    visit_count = models.PositiveIntegerField(default=0, editable=False)
    STATUS_CHOICES = (
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="enabled")

    panels = [
        FieldPanel('name'),
        FieldPanel('status'),
        InlinePanel(
            'personalisation_timerule_related',
            label="Time rule",
            min_num=0,
            max_num=1
        ),
        InlinePanel(
            'personalisation_referralrule_related',
            label="Referral rule",
            min_num=0,
            max_num=1
        ),
        InlinePanel(
            'personalisation_visitcountrule_related',
            label="Visit count rule",
            min_num=0,
            max_num=1
        ),
    ]

    def __str__(self):
        return self.name

    def encoded_name(self):
        """Returns a string with a slug for the segment"""
        return slugify(self.name.lower())


def check_status_change(sender, instance, *args, **kwargs):
    """Check if the status has changed. Alter dates accordingly."""
    try:
        original_status = sender.objects.get(pk=instance.id).status
    except sender.DoesNotExist:
        original_status = ""

    if original_status != instance.status:
        if instance.status == "enabled":
            instance.enable_date = datetime.now()
            instance.visit_count = 0
            return instance
        if instance.status == "disabled":
            instance.disable_date = datetime.now()

pre_save.connect(check_status_change, sender=Segment)


class AdminPersonalisablePageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super(AdminPersonalisablePageForm, self).__init__(*args, **kwargs)
        self.current_segment = Segment.objects.first() # TODO: Filter for the current segment

    def save(self, commit=True):
        page = super(AdminPersonalisablePageForm, self).save(commit=False)

        if page.segment:
            segment = page.segment
            slug = "{}-{}".format(page.slug, segment.encoded_name())
            title = "{} ({})".format(page.title, segment.name)
            update_attrs = {
                'title': title,
                'slug': slug,
                'segment': segment,
                'live': False,
                'canonical_page': page,
            }

            # TODO: Implement logic to change segment when there's already one set instead of copying

            new_page = page.copy(update_attrs=update_attrs, copy_revisions=False)

            return new_page
        page.save()

        return page


class PersonalisablePage(Page):
    canonical_page = models.ForeignKey(
        'self', related_name='variations', on_delete=models.SET_NULL,
        blank=True, null=True
    )
    segment = models.ForeignKey(
        Segment, related_name='segments', on_delete=models.PROTECT,
        blank=True, null=True
    )

    variation_panels = [
        MultiFieldPanel([
            FieldPanel('segment'),
            # TOOD: Currently the user can only select pages of the 'PersonalisablePage' type.
            # This is no longer acceptable as soon as a page inherits the 'PersonalisablePage'.
            PageChooserPanel('canonical_page', page_type=None),
        ])
    ]

    base_form_class = AdminPersonalisablePageForm

    def __str__(self):
        return "{} ({})".format(self.title, self.segment)

    def get_variations(self, only_live=True):
        canonical_page = self.canonical_page or self
        variations = PersonalisablePage.objects.filter(
            Q(canonical_page=canonical_page) |
            Q(pk=canonical_page.pk)
        ).exclude(pk=self.pk)

        if only_live:
            variations = variations.live()

        return variations

    def get_variation_parent(self, segment):
        site = self.get_site()

        variation_parent = (
            PersonalisablePage.objects
            .filter(
                canonical_page=self.get_parent(),
                segment=segment,
                path__startswith=site.root_page.path,
            ).first()
        )
        return variation_parent

    def create_variation(self, segment, copy_fields=False, parent=None):
        slug = "{}-{}".format(self.slug, segment.encoded_name())

        if not parent:
            parent = self.get_variation_parent(segment)

        update_attrs = {
            'title': self.title,
            'slug': slug,
            'segment': segment,
            'live': False,
            'canonical_page': self,
        }

        if copy_fields:
            kwargs = {'update_attrs': update_attrs}
            if parent != self.get_parent():
                kwargs['to'] = parent

            new_page = self.copy(**kwargs)
        else:
            model_class = self.content_type.model_class()
            new_page = model_class(**update_attrs)
            parent.add_child(instance=new_page)

        return new_page

    @cached_property
    def has_variations(self):
        return self.variations.exists()

    @cached_property
    def is_canonical(self):
        return not self.canonical_page and self.has_variations


@cached_classmethod
def get_edit_handler(cls):
    tabs = []
    if cls.content_panels:
        tabs.append(ObjectList(cls.content_panels, heading=_("Content")))
    if cls.variation_panels:
        tabs.append(ObjectList(cls.variation_panels, heading=_("Variations")))
    if cls.promote_panels:
        tabs.append(ObjectList(cls.promote_panels, heading=_("Promote")))
    if cls.settings_panels:
        tabs.append(ObjectList(cls.settings_panels, heading=_("Settings"), classname='settings'))

    edit_handler = TabbedInterface(tabs, base_form_class=cls.base_form_class)
    return edit_handler.bind_to_model(cls)


PersonalisablePage.get_edit_handler = get_edit_handler
