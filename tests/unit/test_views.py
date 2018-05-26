import pytest
from django.urls import reverse

from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import VisitCountRule


@pytest.mark.django_db
def test_segment_user_data_view_requires_admin_access(site, client, django_user_model):
    user = django_user_model.objects.create(username='first')

    segment = Segment(type=Segment.TYPE_STATIC, count=1)
    segment.save()

    client.force_login(user)
    url = reverse('segment:segment_user_data', args=(segment.id,))
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == '/admin/login/?next=%s' % url


@pytest.mark.django_db
def test_segment_user_data_view(site, client, mocker, django_user_model):
    user1 = django_user_model.objects.create(username='first')
    user2 = django_user_model.objects.create(username='second')
    admin_user = django_user_model.objects.create(
        username='admin', is_superuser=True)

    segment = Segment(type=Segment.TYPE_STATIC, count=1)
    segment.save()
    segment.static_users.add(user1)
    segment.static_users.add(user2)

    rule1 = VisitCountRule(counted_page=site.root_page, segment=segment)
    rule2 = VisitCountRule(counted_page=site.root_page.get_last_child(),
                           segment=segment)
    rule1.save()
    rule2.save()

    mocker.patch('wagtail_personalisation.rules.VisitCountRule.get_user_info_string',
                 side_effect=[3, 9, 0, 1])

    client.force_login(admin_user)
    response = client.get(
        reverse('segment:segment_user_data', args=(segment.id,)))

    assert response.status_code == 200
    data_lines = response.content.decode().split("\n")

    assert data_lines[0] == 'Username,Visit count - Test page,Visit count - Regular page\r'
    assert data_lines[1] == 'first,3,9\r'
    assert data_lines[2] == 'second,0,1\r'
