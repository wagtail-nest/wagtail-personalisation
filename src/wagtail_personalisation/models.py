from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db import models, transaction
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel)
from wagtail.wagtailcore.models import Page

from wagtail_personalisation.rules import AbstractBaseRule
from wagtail_personalisation.utils import count_active_days


@register_setting(icon='fa-magic')
class PersonalisationSettings(BaseSetting):
    detailed_visits = models.BooleanField(
        default=False,
        help_text=_('Enable to gather more detailed metadata about the visits '
                    'to your segments and the rules that matched. '
                    'Please note that this will create additional load on your '
                    'database. Usage of caching is recommended.'))
    reverse_match = models.BooleanField(
        default=False,
        help_text=_('Enable to reverse match past visits with users as soon as '
                    'a user logs in. This will ensure your data is as complete '
                    'as possible.'))

    panels = [
        MultiFieldPanel([
            FieldPanel('detailed_visits'),
            FieldPanel('reverse_match'),
        ], heading='Analytics'
        )
    ]


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

    name = models.CharField(max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    enable_date = models.DateTimeField(null=True, editable=False)
    disable_date = models.DateTimeField(null=True, editable=False)
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
                    "{}_related".format(rule_model._meta.db_table),
                    label=rule_model._meta.verbose_name,
                ) for rule_model in AbstractBaseRule.__subclasses__()
            ], heading=_("Rules")),
        ]

        super(Segment, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def encoded_name(self):
        """Return a string with a slug for the segment."""
        return slugify(self.name.lower())

    @property
    def active_days(self):
        """Return the amount of days the segment has been active."""
        return count_active_days(self.enable_date, self.disable_date)

    def get_visits(self):
        """Return the segment visits."""
        return SegmentVisit.objects.filter(segments=self)

    @property
    def visit_count(self):
        """Returns the total amount of segment visits."""
        return self.get_visits().count()

    def get_serves(self):
        return SegmentVisit.objects.filter(served_segment=self)

    @property
    def serve_count(self):
        return self.get_serves().count()

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


class SegmentVisitMetadata(models.Model):
    visit = models.ForeignKey(
        'wagtail_personalisation.SegmentVisit', on_delete=models.CASCADE)
    segment = models.ForeignKey(
        'wagtail_personalisation.Segment', on_delete=models.SET_NULL, null=True)
    matched_rules = models.CharField(max_length=2048)


class SegmentVisit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    page = models.ForeignKey(Page, on_delete=models.SET_NULL, null=True)
    segments = models.ManyToManyField(Segment, through=SegmentVisitMetadata)
    served_segment = models.ForeignKey(
        Segment, on_delete=models.CASCADE,
        related_name='served_segment', null=True)
    served_variant = models.ForeignKey(
        Page, on_delete=models.SET_NULL,
        related_name='served_variant', null=True)
    session = models.CharField(
        max_length=64, editable=False, null=True, db_index=True)
    visit_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date']

    @classmethod
    def create_segment_visit(cls, page, request, metadata=None):
        """Create a segment visit object.
        :param page: The page being visited
        :type page: wagtail.wagtailcore.models.Page
        :param request: The http request
        :type request: django.http.HttpRequest
        :param metadata: A list of personalisable page metadata
        :type page: wagtail_personalisation.models.PersonalisablePageMetadata
        :returns: A committed Segment Visit object
        :rtype: wagtail_personalisation.models.SegmentVisit
        """
        from wagtail_personalisation.adapters import get_segment_adapter
        wxp_settings = PersonalisationSettings.for_site(request.site)

        if wxp_settings.detailed_visits:
            adapter = get_segment_adapter(request)
            user_segments = adapter.get_segments()

            if not metadata:
                metadata = page.personalisation_metadata
                metadata = metadata.metadata_for_segments(user_segments)

            user = request.user if request.user.is_authenticated else None
            visit = cls.objects.create(
                user=user,
                page=page,
                served_segment=metadata.first().segment,
                served_variant=metadata.first().variant,
                session=request.session.session_key
            )

            for segment in user_segments:
                rules = [
                    rule for rule in segment.get_rules() if rule.unique_encoded_name
                    in request.matched_rules
                ]

                SegmentVisitMetadata.objects.create(
                    visit=visit,
                    segment=segment,
                    matched_rules=','.join(
                        rule.unique_encoded_name for rule in rules)
                )

            return visit

    @classmethod
    def reverse_match(cls, user):
        user_visits = cls.objects.filter(user=user)

        for visit in user_visits:
            cls.objects.filter(
                session=visit.session,
                user__isnull=True
            ).update(user=user)


def reverse_match(sender, request, user, **kwargs):
    wxp_settings = PersonalisationSettings.for_site(request.site)
    if wxp_settings.detailed_visits and wxp_settings.reverse_match:
        SegmentVisit.reverse_match(user)

user_logged_in.connect(reverse_match)


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
