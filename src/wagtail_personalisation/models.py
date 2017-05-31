from __future__ import absolute_import, unicode_literals

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.utils.decorators import cached_classmethod
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, ObjectList,
    PageChooserPanel, TabbedInterface)

from wagtail_personalisation.forms import AdminPersonalisablePageForm
from wagtail_personalisation.rules import AbstractBaseRule
from wagtail_personalisation.utils import count_active_days


class SegmentQuerySet(models.QuerySet):
    def enabled(self):
        return self.filter(status=self.model.STATUS_ENABLED)


@python_2_unicode_compatible
class Segment(ClusterableModel):
    """The segment model."""
    STATUS_ENABLED = 'enabled'
    STATUS_DISABLED = 'disabled'

    STATUS_CHOICES = (
        (STATUS_ENABLED, 'Enabled'),
        (STATUS_DISABLED, 'Disabled'),
    )

    name = models.CharField(max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    enable_date = models.DateTimeField(null=True, editable=False)
    disable_date = models.DateTimeField(null=True, editable=False)
    visit_count = models.PositiveIntegerField(default=0, editable=False)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ENABLED)
    persistent = models.BooleanField(
        default=False, help_text=_("Should the segment persist between visits?"))
    match_any = models.BooleanField(
        default=False,
        help_text=_("Should the segment match all the rules or just one of them?")
    )

    objects = SegmentQuerySet.as_manager()

    def __init__(self, *args, **kwargs):
        Segment.panels = [
            MultiFieldPanel([
                FieldPanel('name', classname="title"),
                FieldRowPanel([
                    FieldPanel('status'),
                    FieldPanel('persistent'),
                ]),
                FieldPanel('match_any'),
            ], heading="Segment"),
            MultiFieldPanel([
                InlinePanel(
                    "{}_related".format(rule._meta.db_table),
                    label=rule.__str__,
                ) for rule in AbstractBaseRule.__subclasses__()
            ], heading="Rules"),
        ]

        super(Segment, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def encoded_name(self):
        """Return a string with a slug for the segment."""
        return slugify(self.name.lower())

    def get_active_days(self):
        """Return the amount of days the segment has been active."""
        return count_active_days(self.enable_date, self.disable_date)

    def get_rules(self):
        """Retrieve all rules in the segment."""
        rules = AbstractBaseRule.__subclasses__()
        segment_rules = []
        for rule in rules:
            segment_rules += rule.objects.filter(segment=self)
        return segment_rules


class PersonalisablePageMixin(models.Model):
    """The personalisable page model. Allows creation of variants with linked
    segments.

    """

    class Meta:
        abstract = True

    canonical_page = models.ForeignKey(
        'self', related_name='variations', on_delete=models.SET_NULL,
        blank=True, null=True
    )
    segment = models.ForeignKey(
        Segment, related_name='+', on_delete=models.PROTECT,
        blank=True, null=True
    )
    is_segmented = models.BooleanField(default=False)

    variation_panels = [
        MultiFieldPanel([
            FieldPanel('segment'),
            PageChooserPanel('canonical_page', page_type=None),
        ])
    ]

    base_form_class = AdminPersonalisablePageForm

    def __str__(self):
        return "{}".format(self.title)

    @cached_property
    def has_variations(self):
        """Return a boolean indicating whether or not the personalisable page
        has variations.

        :returns: A boolean indicating whether or not the personalisable page
                  has variations.
        :rtype: bool

        """
        return self.variations.exists()

    @cached_property
    def is_canonical(self):
        """Return a boolean indicating whether or not the personalisable page
        is a canonical page.

        :returns: A boolean indicating whether or not the personalisable page
                  is a canonical page.
        :rtype: bool

        """
        return not self.canonical_page and self.has_variations

    def copy_for_segment(self, segment):
        slug = "{}-{}".format(self.slug, segment.encoded_name())
        title = "{} ({})".format(self.title, segment.name)
        update_attrs = {
            'title': title,
            'slug': slug,
            'segment': segment,
            'live': False,
            'canonical_page': self,
            'is_segmented': True,
        }

        return self.copy(update_attrs=update_attrs, copy_revisions=False)

    def variants_for_segments(self, segments):
        return self.__class__.objects.filter(
            canonical_page=self, segment__in=segments)


@cached_classmethod
def get_edit_handler(cls):
    """Add additional edit handlers to pages that are allowed to have
    variations.

    """
    tabs = []
    if cls.content_panels:
        tabs.append(ObjectList(cls.content_panels, heading=_("Content")))
    if cls.variation_panels:
        tabs.append(ObjectList(cls.variation_panels, heading=_("Variations")))
    if cls.promote_panels:
        tabs.append(ObjectList(cls.promote_panels, heading=_("Promote")))
    if cls.settings_panels:
        tabs.append(ObjectList(cls.settings_panels, heading=_("Settings"),
                               classname='settings'))

    edit_handler = TabbedInterface(tabs, base_form_class=cls.base_form_class)
    return edit_handler.bind_to_model(cls)


PersonalisablePageMixin.get_edit_handler = get_edit_handler
