from __future__ import absolute_import, unicode_literals

from django import forms
from django.conf import settings
from django.contrib.sessions.models import Session
from django.db import models, transaction
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.wagtailcore.models import Page

from wagtail_personalisation.rules import AbstractBaseRule
from wagtail_personalisation.utils import count_active_days

from .forms import SegmentAdminForm


class SegmentQuerySet(models.QuerySet):
    def enabled(self):
        return self.filter(status=self.model.STATUS_ENABLED)


@python_2_unicode_compatible
class Segment(ClusterableModel):
    """The segment model."""
    STATUS_ENABLED = 'enabled'
    STATUS_DISABLED = 'disabled'

    STATUS_CHOICES = (
        (STATUS_ENABLED, _('Enabled')),
        (STATUS_DISABLED, _('Disabled')),
    )

    TYPE_DYNAMIC = 'dynamic'
    TYPE_STATIC = 'static'

    TYPE_CHOICES = (
        (TYPE_DYNAMIC, _('Dynamic')),
        (TYPE_STATIC, _('Static')),
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
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_DYNAMIC,
        help_text=mark_safe(_("""
            </br></br><strong>Dynamic:</strong> Users in this segment will change
            as more or less meet the rules specified in the segment.
            </br><strong>Static:</strong> If the segment contains only static
            compatible rules the segment will contain the members that pass
            those rules when the segment is created. Mixed static segments or
            those containing entirely non static compatible rules will be
            populated using the count variable.
        """))
    )
    count = models.PositiveSmallIntegerField(
        default=0,
        help_text=_(
            "If this number is set for a static segment users will be added to the "
            "set until the number is reached. After this no more users will be added."
        )
    )
    static_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
    )

    objects = SegmentQuerySet.as_manager()

    base_form_class = SegmentAdminForm

    def __init__(self, *args, **kwargs):
        Segment.panels = [
            MultiFieldPanel([
                FieldPanel('name', classname="title"),
                FieldRowPanel([
                    FieldPanel('status'),
                    FieldPanel('persistent'),
                ]),
                FieldPanel('match_any'),
                FieldPanel('type', widget=forms.RadioSelect),
                FieldPanel('count', classname='count_field'),
            ], heading="Segment"),
            MultiFieldPanel([
                InlinePanel(
                    "{}_related".format(rule_model._meta.db_table),
                    label='{}{}'.format(
                        rule_model._meta.verbose_name,
                        ' ({})'.format(_('Static compatible')) if rule_model.static else ''
                    ),
                ) for rule_model in AbstractBaseRule.__subclasses__()
            ], heading=_("Rules")),
        ]

        super(Segment, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_static(self):
        return self.type == self.TYPE_STATIC

    @classmethod
    def all_static(cls, rules):
       return all(rule.static for rule in rules)

    @property
    def all_rules_static(self):
        rules = self.get_rules()
        return rules and self.all_static(rules)

    @property
    def is_full(self):
        return self.static_users.count() >= self.count

    def encoded_name(self):
        """Return a string with a slug for the segment."""
        return slugify(self.name.lower())

    def get_active_days(self):
        """Return the amount of days the segment has been active."""
        return count_active_days(self.enable_date, self.disable_date)

    def get_used_pages(self):
        """Return the pages that have variants using this segment."""
        pages = list(PersonalisablePageMetadata.objects.filter(segment=self))

        return pages

    def get_created_variants(self):
        """Return the variants using this segment."""
        pages = Page.objects.filter(_personalisable_page_metadata__segment=self)

        return pages

    def get_rules(self):
        """Retrieve all rules in the segment."""
        segment_rules = []
        for rule_model in AbstractBaseRule.get_descendant_models():
            segment_rules.extend(
                rule_model._default_manager.filter(segment=self))

        return segment_rules

    def toggle(self, save=True):
        self.status = (
            self.STATUS_ENABLED if self.status == self.STATUS_DISABLED
            else self.STATUS_DISABLED)
        if save:
            self.save()


class PersonalisablePageMetadata(ClusterableModel):
    """The personalisable page model. Allows creation of variants with linked
    segments.

    """
    canonical_page = models.ForeignKey(
        Page, related_name='personalisable_canonical_metadata',
        on_delete=models.SET_NULL,
        blank=True, null=True
    )

    variant = models.OneToOneField(
        Page, related_name='_personalisable_page_metadata')

    segment = models.ForeignKey(
        Segment, related_name='page_metadata', null=True, blank=True)

    @cached_property
    def has_variants(self):
        """Return a boolean indicating whether or not the personalisable page
        has variants.

        :returns: A boolean indicating whether or not the personalisable page
                  has variants.
        :rtype: bool

        """
        return self.variants_metadata.exists()

    @cached_property
    def variants_metadata(self):
        return (
            PersonalisablePageMetadata.objects
            .filter(canonical_page_id=self.canonical_page_id)
            .exclude(variant_id=self.variant_id)
            .exclude(variant_id=self.canonical_page_id))

    @cached_property
    def is_canonical(self):
        """Return a boolean indicating whether or not the personalisable page
        is a canonical page.

        :returns: A boolean indicating whether or not the personalisable
        page
                  is a canonical page.
        :rtype: bool

        """
        return self.canonical_page_id == self.variant_id

    def copy_for_segment(self, segment):
        page = self.canonical_page

        slug = "{}-{}".format(page.slug, segment.encoded_name())
        title = "{} ({})".format(page.title, segment.name)
        update_attrs = {
            'title': title,
            'slug': slug,
            'live': False,
        }

        with transaction.atomic():
            new_page = self.canonical_page.copy(
                update_attrs=update_attrs, copy_revisions=False)

            PersonalisablePageMetadata.objects.create(
                canonical_page=page,
                variant=new_page,
                segment=segment)
        return new_page

    def metadata_for_segments(self, segments):
        return (
            self.__class__.objects
            .filter(
                canonical_page_id=self.canonical_page_id,
                segment__in=segments))

    def get_unused_segments(self):
        if self.is_canonical:
            return (
                Segment.objects
                .exclude(page_metadata__canonical_page_id=self.canonical_page_id))
        return Segment.objects.none()


class PersonalisablePageMixin(object):
    """The personalisable page model. Allows creation of variants with linked
    segments.

    """

    @cached_property
    def personalisation_metadata(self):
        try:
            metadata = self._personalisable_page_metadata
        except AttributeError:
            metadata = PersonalisablePageMetadata.objects.create(
                canonical_page=self, variant=self)
        return metadata
