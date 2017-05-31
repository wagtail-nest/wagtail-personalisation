from wagtail.wagtailadmin.forms import WagtailAdminPageForm


class AdminPersonalisablePageForm(WagtailAdminPageForm):
    """The personalisable page form that allows creation of variants."""

    def save(self, commit=True):
        """Save a copy of the original page, linked to a segment.

        :returns: The original page, or a new page.
        :rtype: wagtail_personalisation.models.PersonalisablePage

        """
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
