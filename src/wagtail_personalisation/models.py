import random

import wagtail
from django import forms
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.template.defaultfilters import slugify
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION >= (3, 0):
    from wagtail.admin.panels import (
        FieldPanel,
        FieldRowPanel,
        InlinePanel,
        MultiFieldPanel,
    )
    from wagtail.models import Page
else:
    from wagtail.admin.edit_handlers import (
        FieldPanel,
        FieldRowPanel,
        InlinePanel,
        MultiFieldPanel,
    )
    from wagtail.core.models import Page

from wagtail_personalisation.rules import AbstractBaseRule
from wagtail_personalisation.utils import count_active_days

from .forms import SegmentAdminForm


class RulePanel(InlinePanel):
    def on_model_bound(self):
        self.relation_name = self.relation_name.replace("_related", "s")
        self.db_field = self.model._meta.get_field(self.relation_name)
        manager = getattr(self.model, self.relation_name)
        self.related = manager.rel


class SegmentQuerySet(models.QuerySet):
    def enabled(self):
        return self.filter(status=self.model.STATUS_ENABLED)


class Segment(ClusterableModel):
    """The segment model."""

    STATUS_ENABLED = "enabled"
    STATUS_DISABLED = "disabled"

    STATUS_CHOICES = (
        (STATUS_ENABLED, _("Enabled")),
        (STATUS_DISABLED, _("Disabled")),
    )

    TYPE_DYNAMIC = "dynamic"
    TYPE_STATIC = "static"

    TYPE_CHOICES = (
        (TYPE_DYNAMIC, _("Dynamic")),
        (TYPE_STATIC, _("Static")),
    )

    name = models.CharField(max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    enable_date = models.DateTimeField(null=True, editable=False)
    disable_date = models.DateTimeField(null=True, editable=False)
    visit_count = models.PositiveIntegerField(default=0, editable=False)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ENABLED
    )
    persistent = models.BooleanField(
        default=False, help_text=_("Should the segment persist between visits?")
    )
    match_any = models.BooleanField(
        default=False,
        help_text=_("Should the segment match all the rules or just one of them?"),
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_DYNAMIC,
        help_text=mark_safe(
            _(
                """
            </br></br><strong>Dynamic:</strong> Users in this segment will change
            as more or less meet the rules specified in the segment.
            </br><strong>Static:</strong> If the segment contains only static
            compatible rules the segment will contain the members that pass
            those rules when the segment is created. Mixed static segments or
            those containing entirely non static compatible rules will be
            populated using the count variable.
        """
            )
        ),
    )
    count = models.PositiveSmallIntegerField(
        default=0,
        help_text=_(
            "If this number is set for a static segment users will be added to the "
            "set until the number is reached. After this no more users will be added."
        ),
    )
    static_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
    )
    excluded_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        help_text=_(
            "Users that matched the rules but were excluded from the "
            "segment for some reason e.g. randomisation"
        ),
        related_name="excluded_segments",
    )

    matched_users_count = models.PositiveIntegerField(default=0, editable=False)
    matched_count_updated_at = models.DateTimeField(null=True, editable=False)

    randomisation_percent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        default=None,
        help_text=_(
            "If this number is set each user matching the rules will "
            "have this percentage chance of being placed in the segment."
        ),
        validators=[MaxValueValidator(100), MinValueValidator(0)],
    )

    objects = SegmentQuerySet.as_manager()

    base_form_class = SegmentAdminForm

    def __init__(self, *args, **kwargs):
        Segment.panels = [
            MultiFieldPanel(
                [
                    FieldPanel("name", classname="title"),
                    FieldRowPanel(
                        [
                            FieldPanel("status"),
                            FieldPanel("persistent"),
                        ]
                    ),
                    FieldPanel("match_any"),
                    FieldPanel("type", widget=forms.RadioSelect),
                    FieldPanel("count", classname="count_field"),
                    FieldPanel("randomisation_percent", classname="percent_field"),
                ],
                heading="Segment",
            ),
            MultiFieldPanel(
                [
                    RulePanel(
                        "{}_related".format(rule_model._meta.db_table),
                        label="{}{}".format(
                            rule_model._meta.verbose_name,
                            " ({})".format(_("Static compatible"))
                            if rule_model.static
                            else "",
                        ),
                    )
                    for rule_model in AbstractBaseRule.__subclasses__()
                ],
                heading=_("Rules"),
            ),
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
        return PersonalisablePageMetadata.objects.filter(segment=self)

    def get_created_variants(self):
        """Return the variants using this segment."""
        return Page.objects.filter(_personalisable_page_metadata__segment=self)

    def get_rules(self):
        """Retrieve all rules in the segment."""
        segment_rules = []
        for rule_model in AbstractBaseRule.get_descendant_models():
            segment_rules.extend(rule_model._default_manager.filter(segment=self))

        return segment_rules

    def toggle(self, save=True):
        self.status = (
            self.STATUS_ENABLED
            if self.status == self.STATUS_DISABLED
            else self.STATUS_DISABLED
        )
        if save:
            self.save()

    def randomise_into_segment(self):
        """Returns True if randomisation_percent is not set or it generates
        a random number less than the randomisation_percent
        This is so there is some randomisation in which users are added to the
        segment
        """
        if self.randomisation_percent is None:
            return True

        if random.randint(1, 100) <= self.randomisation_percent:
            return True
        return False


class PersonalisablePageMetadata(ClusterableModel):
    """The personalisable page model. Allows creation of variants with linked
    segments.

    """

    # Canonical pages should not ever be deleted if they have variants
    # because the variants will be orphaned.
    canonical_page = models.ForeignKey(
        Page,
        models.PROTECT,
        related_name="personalisable_canonical_metadata",
        null=True,
    )

    # Delete metadata of the variant if its page gets deleted.
    variant = models.OneToOneField(
        Page, models.CASCADE, related_name="_personalisable_page_metadata", null=True
    )

    segment = models.ForeignKey(
        Segment, models.PROTECT, null=True, related_name="page_metadata"
    )

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
            PersonalisablePageMetadata.objects.filter(
                canonical_page_id=self.canonical_page_id
            )
            .exclude(variant_id=self.variant_id)
            .exclude(variant_id=self.canonical_page_id)
        )

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
            "title": title,
            "slug": slug,
            "live": False,
        }

        with transaction.atomic():
            new_page = self.canonical_page.copy(
                update_attrs=update_attrs, copy_revisions=False
            )

            PersonalisablePageMetadata.objects.create(
                canonical_page=page, variant=new_page, segment=segment
            )
        return new_page

    def metadata_for_segments(self, segments):
        return self.__class__.objects.filter(
            canonical_page_id=self.canonical_page_id, segment__in=segments
        )

    def get_unused_segments(self):
        if self.is_canonical:
            return Segment.objects.exclude(
                page_metadata__canonical_page_id=self.canonical_page_id
            )
        return Segment.objects.none()


class PersonalisablePageMixin:
    """The personalisable page model. Allows creation of variants with linked
    segments.

    """

    @cached_property
    def personalisation_metadata(self):
        try:
            metadata = self._personalisable_page_metadata
        except AttributeError:
            metadata = PersonalisablePageMetadata.objects.create(
                canonical_page=self, variant=self
            )
        return metadata

    def get_sitemap_urls(self, request=None):
        # Do not generate sitemap entries for variants.
        if not self.personalisation_metadata.is_canonical:
            return []
        if wagtail.VERSION >= (2, 2):
            # Since Wagtail 2.2 you can pass request to the get_sitemap_urls
            # method.
            return super(PersonalisablePageMixin, self).get_sitemap_urls(
                request=request
            )
        return super(PersonalisablePageMixin, self).get_sitemap_urls()
