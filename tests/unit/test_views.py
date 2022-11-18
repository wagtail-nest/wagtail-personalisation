import pytest
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from wagtail.core.models import Page

from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import VisitCountRule
from wagtail_personalisation.views import SegmentModelAdmin, SegmentModelDeleteView


@pytest.mark.django_db
def test_segment_user_data_view_requires_admin_access(site, client, django_user_model):
    user = django_user_model.objects.create(username="first")

    segment = Segment(type=Segment.TYPE_STATIC, count=1)
    segment.save()

    client.force_login(user)
    url = reverse("segment:segment_user_data", args=(segment.id,))
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == "/admin/login/?next=%s" % url


@pytest.mark.django_db
def test_segment_user_data_view(site, client, mocker, django_user_model):
    user1 = django_user_model.objects.create(username="first")
    user2 = django_user_model.objects.create(username="second")
    admin_user = django_user_model.objects.create(username="admin", is_superuser=True)

    segment = Segment(type=Segment.TYPE_STATIC, count=1)
    segment.save()
    segment.static_users.add(user1)
    segment.static_users.add(user2)

    rule1 = VisitCountRule(counted_page=site.root_page, segment=segment)
    rule2 = VisitCountRule(
        counted_page=site.root_page.get_last_child(), segment=segment
    )
    rule1.save()
    rule2.save()

    mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.get_user_info_string",
        side_effect=[3, 9, 0, 1],
    )

    client.force_login(admin_user)
    response = client.get(reverse("segment:segment_user_data", args=(segment.id,)))

    assert response.status_code == 200
    data_lines = response.content.decode().split("\n")

    assert (
        data_lines[0] == "Username,Visit count - Test page,Visit count - Regular page\r"
    )
    assert data_lines[1] == "first,3,9\r"
    assert data_lines[2] == "second,0,1\r"


@pytest.mark.django_db
def test_segment_delete_view_delete_instance(rf, segmented_page, user):
    user.is_superuser = True
    user.save()
    segment = segmented_page.personalisation_metadata.segment
    canonical_page = segmented_page.personalisation_metadata.canonical_page
    variants_metadata = segment.get_used_pages()
    page_variants = Page.objects.filter(
        pk__in=(variants_metadata.values_list("variant_id", flat=True))
    )

    # Make sure all canonical page, variants and variants metadata exist
    assert canonical_page
    assert page_variants
    assert variants_metadata

    # Delete the segment via the method on the view.
    request = rf.get("/".format(segment.pk))  # noqa: F523
    request.user = user
    view = SegmentModelDeleteView(
        instance_pk=str(segment.pk), model_admin=SegmentModelAdmin()
    )
    view.request = request
    view.delete_instance()

    # Segment has been deleted.
    with pytest.raises(segment.DoesNotExist):
        segment.refresh_from_db()

    # Canonical page stayed intact.
    canonical_page.refresh_from_db()

    # Variant pages and their metadata have been deleted.
    assert not page_variants.all()
    assert not variants_metadata.all()


@pytest.mark.django_db
def test_segment_delete_view_raises_permission_denied(rf, segmented_page, user):
    segment = segmented_page.personalisation_metadata.segment
    request = rf.get("/".format(segment.pk))  # noqa: F523
    request.user = user
    view = SegmentModelDeleteView(
        instance_pk=str(segment.pk), model_admin=SegmentModelAdmin()
    )
    view.request = request
    message = "User have no permission to delete variant page objects."  # noqa: F841
    with pytest.raises(PermissionDenied):
        view.delete_instance()
