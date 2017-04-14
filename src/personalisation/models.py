from __future__ import absolute_import, unicode_literals

from django.db import models
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.utils.decorators import cached_classmethod
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, ObjectList,
    PageChooserPanel, TabbedInterface)
from wagtail.wagtailadmin.forms import WagtailAdminPageForm
from wagtail.wagtailcore.models import Page

from personalisation.rules import AbstractBaseRule


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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default="enabled")
    persistent = models.BooleanField(
        default=False, help_text=_("Should the segment persist between visits?"))
    match_any = models.BooleanField(
        default=False,
        help_text=_("Should the segment match all the rules or just one of them?")
    )

    panels = [
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

    def __str__(self):
        return self.name

    def encoded_name(self):
        """Returns a string with a slug for the segment"""
        return slugify(self.name.lower())

    def get_rules(self):
        rules = AbstractBaseRule.__subclasses__()
        segment_rules = []
        for rule in rules:
            segment_rules += rule.objects.filter(segment=self)
        return segment_rules


def check_status_change(sender, instance, *args, **kwargs):
    """Check if the status has changed. Alter dates accordingly."""
    try:
        original_status = sender.objects.get(pk=instance.id).status
    except sender.DoesNotExist:
        original_status = ""

    if original_status != instance.status:
        if instance.status == "enabled":
            instance.enable_date = timezone.now()
            instance.visit_count = 0
            return instance
        if instance.status == "disabled":
            instance.disable_date = timezone.now()


pre_save.connect(check_status_change, sender=Segment)


class AdminPersonalisablePageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super(AdminPersonalisablePageForm, self).__init__(*args, **kwargs)

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
                'is_segmented': True,
            }

            if page.is_segmented:
                slug = "{}-{}".format(
                    page.canonical_page.slug, segment.encoded_name())
                title = "{} ({})".format(
                    page.canonical_page.title, segment.name)
                page.slug = slug
                page.title = title
                page.save()
                return page
            else:
                new_page = page.copy(
                    update_attrs=update_attrs, copy_revisions=False)
                return new_page

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
        tabs.append(ObjectList(cls.settings_panels, heading=_("Settings"),
                               classname='settings'))

    edit_handler = TabbedInterface(tabs, base_form_class=cls.base_form_class)
    return edit_handler.bind_to_model(cls)


PersonalisablePage.get_edit_handler = get_edit_handler
