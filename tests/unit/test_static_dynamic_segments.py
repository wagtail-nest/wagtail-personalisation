from __future__ import absolute_import, unicode_literals

import datetime

import pytest
from django.forms.models import model_to_dict

from tests.factories.segment import SegmentFactory
from wagtail_personalisation.forms import SegmentAdminForm
from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import TimeRule, VisitCountRule


def form_with_data(segment, *rules):
    model_fields = [
        "type",
        "status",
        "count",
        "name",
        "match_any",
        "randomisation_percent",
    ]
    model_formsets = [
        "wagtail_personalisation_timerules",
        "wagtail_personalisation_dayrules",
        "wagtail_personalisation_referralrules",
        "wagtail_personalisation_visitcountrules",
        "wagtail_personalisation_queryrules",
        "wagtail_personalisation_devicerules",
        "wagtail_personalisation_userisloggedinrules",
        "wagtail_personalisation_origincountryrules",
    ]

    class TestSegmentAdminForm(SegmentAdminForm):
        class Meta:
            model = Segment
            fields = model_fields
            formsets = model_formsets

    data = model_to_dict(segment, model_fields)
    for formset in TestSegmentAdminForm().formsets.values():
        rule_data = {}
        count = 0
        for rule in rules:
            if isinstance(rule, formset.model):
                rule_data = model_to_dict(rule)
                for key, value in rule_data.items():
                    data["{}-{}-{}".format(formset.prefix, count, key)] = value
                count += 1
        data["{}-INITIAL_FORMS".format(formset.prefix)] = 0
        data["{}-TOTAL_FORMS".format(formset.prefix)] = count
    return TestSegmentAdminForm(data)


@pytest.mark.django_db
def test_user_added_to_static_segment_at_creation(site, user, mocker):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user", return_value=True
    )
    instance = form.save()

    assert user in instance.static_users.all()


@pytest.mark.django_db
def test_user_not_added_to_full_static_segment_at_creation(
    site, django_user_model, mocker
):
    django_user_model.objects.create(username="first")
    django_user_model.objects.create(username="second")
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user",
        side_effect=[True, True],
    )
    instance = form.save()

    assert len(instance.static_users.all()) == 1


@pytest.mark.django_db
def test_anonymous_user_not_added_to_static_segment_at_creation(site, client, mocker):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    mock_test_rule = mocker.patch(
        "wagtail_personalisation.adapters.SessionSegmentsAdapter._test_rules"
    )
    instance = form.save()

    assert not instance.static_users.all()
    assert mock_test_rule.call_count == 0


@pytest.mark.django_db
def test_match_any_correct_populates(site, django_user_model, mocker):
    user = django_user_model.objects.create(username="first")
    other_user = django_user_model.objects.create(username="second")
    other_page = site.root_page.get_last_child()

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, match_any=True)
    rule_1 = VisitCountRule(counted_page=site.root_page)
    rule_2 = VisitCountRule(counted_page=other_page)
    form = form_with_data(segment, rule_1, rule_2)
    mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user",
        side_effect=[True, False, True, False],
    )
    instance = form.save()

    assert user in instance.static_users.all()
    assert other_user in instance.static_users.all()


@pytest.mark.django_db
def test_mixed_static_dynamic_session_doesnt_generate_at_creation(site, mocker):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    static_rule = VisitCountRule(counted_page=site.root_page)
    non_static_rule = TimeRule(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
    )
    form = form_with_data(segment, static_rule, non_static_rule)

    mock_test_rule = mocker.patch(
        "wagtail_personalisation.adapters.SessionSegmentsAdapter._test_rules"
    )
    instance = form.save()

    assert not instance.static_users.all()
    assert mock_test_rule.call_count == 0


@pytest.mark.django_db
def test_session_not_added_to_static_segment_after_creation(site, client, user):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=0)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    session = client.session
    session.save()
    client.force_login(user)
    client.get(site.root_page.url)

    assert not instance.static_users.all()


@pytest.mark.django_db
def test_session_added_to_static_segment_after_creation(site, client, user):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    session = client.session
    session.save()
    client.force_login(user)
    client.get(site.root_page.url)

    assert user in instance.static_users.all()


@pytest.mark.django_db
def test_anonymou_user_not_added_to_static_segment_after_creation(site, client):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    session = client.session
    session.save()
    client.get(site.root_page.url)

    assert not instance.static_users.all()


@pytest.mark.django_db
def test_session_not_added_to_static_segment_after_full(
    site, client, django_user_model
):
    user = django_user_model.objects.create(username="first")
    other_user = django_user_model.objects.create(username="second")
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    assert not instance.static_users.all()

    session = client.session
    client.force_login(user)
    client.get(site.root_page.url)

    assert instance.static_users.count() == 1

    client.cookies.clear()
    second_session = client.session
    client.force_login(other_user)
    client.get(site.root_page.url)

    assert session.session_key != second_session.session_key
    assert instance.static_users.count() == 1
    assert user in instance.static_users.all()
    assert other_user not in instance.static_users.all()


@pytest.mark.django_db
def test_sessions_not_added_to_static_segment_if_rule_not_static(mocker):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=1)
    rule = TimeRule(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
        segment=segment,
    )
    form = form_with_data(segment, rule)
    mock_test_rule = mocker.patch(
        "wagtail_personalisation.adapters.SessionSegmentsAdapter._test_rules"
    )
    instance = form.save()

    assert not instance.static_users.all()
    assert mock_test_rule.call_count == 0


@pytest.mark.django_db
def test_does_not_calculate_the_segment_again(site, client, mocker, user):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=2)
    rule = VisitCountRule(counted_page=site.root_page, segment=segment)
    form = form_with_data(segment, rule)
    mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user", return_value=True
    )
    instance = form.save()

    assert user in instance.static_users.all()

    mock_test_rule = mocker.patch(
        "wagtail_personalisation.adapters.SessionSegmentsAdapter._test_rules"
    )
    session = client.session
    session.save()
    client.force_login(user)
    client.get(site.root_page.url)
    assert mock_test_rule.call_count == 0


@pytest.mark.django_db
def test_non_static_rules_have_a_count():
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=0)
    rule = TimeRule(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
        segment=segment,
    )
    form = form_with_data(segment, rule)
    assert not form.is_valid()


@pytest.mark.django_db
def test_static_segment_with_static_rules_needs_no_count(site):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, count=0)
    rule = VisitCountRule(counted_page=site.root_page, segment=segment)
    form = form_with_data(segment, rule)
    assert form.is_valid()


@pytest.mark.django_db
def test_dynamic_segment_with_non_static_rules_have_a_count():
    segment = SegmentFactory.build(type=Segment.TYPE_DYNAMIC, count=0)
    rule = TimeRule(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
    )
    form = form_with_data(segment, rule)
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_randomisation_percentage_added_to_segment_at_creation(
    site, client, mocker, django_user_model
):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    segment.randomisation_percent = 80
    rule = VisitCountRule()

    form = form_with_data(segment, rule)
    instance = form.save()

    assert instance.randomisation_percent == 80


@pytest.mark.django_db
def test_randomisation_percentage_min_zero(site, client, mocker, django_user_model):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    segment.randomisation_percent = -1
    rule = VisitCountRule()

    form = form_with_data(segment, rule)
    assert not form.is_valid()


@pytest.mark.django_db
def test_randomisation_percentage_max_100(site, client, mocker, django_user_model):
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    segment.randomisation_percent = 101
    rule = VisitCountRule()

    form = form_with_data(segment, rule)
    assert not form.is_valid()


@pytest.mark.django_db
def test_in_static_segment_if_random_is_below_percentage(site, client, mocker, user):
    segment = SegmentFactory.build(
        type=Segment.TYPE_STATIC, count=1, randomisation_percent=40
    )
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    mocker.patch("random.randint", return_value=39)
    session = client.session
    session.save()
    client.force_login(user)
    client.get(site.root_page.url)

    assert instance.id == client.session["segments"][0]["id"]
    assert user in instance.static_users.all()
    assert user not in instance.excluded_users.all()


@pytest.mark.django_db
def test_not_in_static_segment_if_random_is_above_percentage(
    site, client, mocker, user
):
    segment = SegmentFactory.build(
        type=Segment.TYPE_STATIC, count=1, randomisation_percent=40
    )
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    mocker.patch("random.randint", return_value=41)
    session = client.session
    session.save()
    client.force_login(user)
    client.get(site.root_page.url)

    assert len(client.session["segments"]) == 0
    assert user not in instance.static_users.all()
    assert user in instance.excluded_users.all()


@pytest.mark.django_db
def test_offered_dynamic_segment_if_random_is_below_percentage(site, client, mocker):
    segment = SegmentFactory.build(type=Segment.TYPE_DYNAMIC, randomisation_percent=40)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    mocker.patch("random.randint", return_value=39)
    session = client.session
    session.save()
    client.get(site.root_page.url)

    assert len(client.session["excluded_segments"]) == 0
    assert instance.id == client.session["segments"][0]["id"]


@pytest.mark.django_db
def test_not_offered_dynamic_segment_if_random_is_above_percentage(
    site, client, mocker
):
    segment = SegmentFactory.build(type=Segment.TYPE_DYNAMIC, randomisation_percent=40)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    mocker.patch("random.randint", return_value=41)
    session = client.session
    session.save()
    client.get(site.root_page.url)

    assert len(client.session["segments"]) == 0
    assert instance.id == client.session["excluded_segments"][0]["id"]


@pytest.mark.django_db
def test_not_in_segment_if_percentage_is_0(site, client, mocker, user):
    segment = SegmentFactory.build(
        type=Segment.TYPE_STATIC, count=1, randomisation_percent=0
    )
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    session = client.session
    session.save()
    client.force_login(user)
    client.get(site.root_page.url)

    assert len(client.session["segments"]) == 0
    assert user not in instance.static_users.all()
    assert user in instance.excluded_users.all()


@pytest.mark.django_db
def test_always_in_segment_if_percentage_is_100(site, client, mocker, user):
    segment = SegmentFactory.build(
        type=Segment.TYPE_STATIC, count=1, randomisation_percent=100
    )
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()

    session = client.session
    session.save()
    client.force_login(user)
    client.get(site.root_page.url)

    assert instance.id == client.session["segments"][0]["id"]
    assert user in instance.static_users.all()
    assert user not in instance.excluded_users.all()


@pytest.mark.django_db
def test_not_added_to_static_segment_at_creation_if_random_above_percent(
    site, mocker, user
):
    mocker.patch("random.randint", return_value=41)
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, randomisation_percent=40)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user", return_value=True
    )
    instance = form.save()

    assert user not in instance.static_users.all()
    assert user in instance.excluded_users.all()


@pytest.mark.django_db
def test_added_to_static_segment_at_creation_if_random_below_percent(
    site, mocker, user
):
    mocker.patch("random.randint", return_value=39)
    segment = SegmentFactory.build(type=Segment.TYPE_STATIC, randomisation_percent=40)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user", return_value=True
    )
    instance = form.save()

    assert user in instance.static_users.all()
    assert user not in instance.excluded_users.all()


@pytest.mark.django_db
def test_rules_check_skipped_if_user_in_excluded(site, client, mocker, user):
    segment = SegmentFactory.build(
        type=Segment.TYPE_STATIC, count=1, randomisation_percent=100
    )
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()
    instance.excluded_users.add(user)
    instance.save

    mock_test_rule = mocker.patch(
        "wagtail_personalisation.adapters.SessionSegmentsAdapter._test_rules"
    )

    session = client.session
    session.save()
    client.force_login(user)
    client.get(site.root_page.url)

    assert mock_test_rule.call_count == 0
    assert len(client.session["segments"]) == 0
    assert user not in instance.static_users.all()
    assert user in instance.excluded_users.all()


@pytest.mark.django_db
def test_rules_check_skipped_if_dynamic_segment_in_excluded(site, client, mocker, user):
    segment = SegmentFactory.build(type=Segment.TYPE_DYNAMIC, randomisation_percent=100)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    instance = form.save()
    instance.persistent = True
    instance.save()

    session = client.session
    session["excluded_segments"] = [{"id": instance.pk}]
    session.save()

    mock_test_rule = mocker.patch(
        "wagtail_personalisation.adapters.SessionSegmentsAdapter._test_rules"
    )

    client.force_login(user)
    client.get(site.root_page.url)

    assert mock_test_rule.call_count == 0
    assert len(client.session["segments"]) == 0


@pytest.mark.django_db
def test_matched_user_count_added_to_segment_at_creation(
    site, mocker, django_user_model
):
    django_user_model.objects.create(username="first")
    django_user_model.objects.create(username="second")

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    rule = VisitCountRule()

    form = form_with_data(segment, rule)
    form.instance.type = Segment.TYPE_STATIC
    mock_test_user = mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user", return_value=True
    )
    instance = form.save()

    assert mock_test_user.call_count == 2
    instance.matched_users_count = 2


@pytest.mark.django_db
def test_count_users_matching_static_rules(site, client, mocker, django_user_model):
    django_user_model.objects.create(username="first")
    django_user_model.objects.create(username="second")

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user", return_value=True
    )

    assert form.count_matching_users([rule], True) == 2


@pytest.mark.django_db
def test_count_matching_users_excludes_staff(site, client, mocker, django_user_model):
    django_user_model.objects.create(username="first")
    django_user_model.objects.create(username="second", is_staff=True)

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    mock_test_user = mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user", return_value=True
    )

    assert form.count_matching_users([rule], True) == 1
    assert mock_test_user.call_count == 1


@pytest.mark.django_db
def test_count_matching_users_excludes_inactive(
    site, client, mocker, django_user_model
):
    django_user_model.objects.create(username="first")
    django_user_model.objects.create(username="second", is_active=False)

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    rule = VisitCountRule(counted_page=site.root_page)
    form = form_with_data(segment, rule)
    mock_test_user = mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user", return_value=True
    )

    assert form.count_matching_users([rule], True) == 1
    assert mock_test_user.call_count == 1


@pytest.mark.django_db
def test_count_matching_users_only_counts_static_rules(
    site, client, mocker, django_user_model
):
    django_user_model.objects.create(username="first")
    django_user_model.objects.create(username="second")

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    rule = TimeRule(
        start_time=datetime.time(0, 0, 0),
        end_time=datetime.time(23, 59, 59),
        segment=segment,
    )
    form = form_with_data(segment, rule)
    mock_test_user = mocker.patch("wagtail_personalisation.rules.TimeRule.test_user")

    assert form.count_matching_users([rule], True) == 0
    assert mock_test_user.call_count == 0


@pytest.mark.django_db
def test_count_matching_users_handles_match_any(
    site, client, mocker, django_user_model
):
    django_user_model.objects.create(username="first")
    django_user_model.objects.create(username="second")

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    first_rule = VisitCountRule(counted_page=site.root_page)
    other_page = site.root_page.get_last_child()
    second_rule = VisitCountRule(counted_page=other_page)
    form = form_with_data(segment, first_rule, second_rule)

    mock_test_user = mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user",
        side_effect=[True, False, True, False],
    )

    assert form.count_matching_users([first_rule, second_rule], True) == 2
    mock_test_user.call_count == 4


@pytest.mark.django_db
def test_count_matching_users_handles_match_all(
    site, client, mocker, django_user_model
):
    django_user_model.objects.create(username="first")
    django_user_model.objects.create(username="second")

    segment = SegmentFactory.build(type=Segment.TYPE_STATIC)
    first_rule = VisitCountRule(counted_page=site.root_page)
    other_page = site.root_page.get_last_child()
    second_rule = VisitCountRule(counted_page=other_page)
    form = form_with_data(segment, first_rule, second_rule)

    mock_test_user = mocker.patch(
        "wagtail_personalisation.rules.VisitCountRule.test_user",
        side_effect=[True, True, False, True],
    )

    assert form.count_matching_users([first_rule, second_rule], False) == 1
    mock_test_user.call_count == 4
