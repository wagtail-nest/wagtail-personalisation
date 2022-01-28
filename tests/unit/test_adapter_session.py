import pytest

from tests.factories.segment import SegmentFactory
from wagtail_personalisation import adapters


@pytest.mark.django_db
def test_get_segments(rf):
    request = rf.get("/")

    adapter = adapters.SessionSegmentsAdapter(request)

    segment_1 = SegmentFactory(name="segment-1", persistent=True)
    segment_2 = SegmentFactory(name="segment-2", persistent=True)

    adapter.set_segments([segment_1, segment_2])
    assert len(request.session["segments"]) == 2

    segments = adapter.get_segments()
    assert segments == [segment_1, segment_2]


@pytest.mark.django_db
def test_get_segments_session(rf):
    request = rf.get("/")

    adapter = adapters.SessionSegmentsAdapter(request)

    segment_1 = SegmentFactory(name="segment-1", persistent=True)
    segment_2 = SegmentFactory(name="segment-2", persistent=True)

    adapter.set_segments([segment_1, segment_2])
    assert len(request.session["segments"]) == 2

    adapter._segment_cache = None
    segments = adapter.get_segments()
    assert segments == [segment_1, segment_2]


@pytest.mark.django_db
def test_get_segment_by_id(rf):
    request = rf.get("/")

    adapter = adapters.SessionSegmentsAdapter(request)

    segment_1 = SegmentFactory(name="segment-1", persistent=True)
    segment_2 = SegmentFactory(name="segment-2", persistent=True)

    adapter.set_segments([segment_1, segment_2])

    segment_x = adapter.get_segment_by_id(segment_2.pk)
    assert segment_x == segment_2


@pytest.mark.django_db
def test_refresh_removes_disabled(rf):
    request = rf.get("/")

    adapter = adapters.SessionSegmentsAdapter(request)

    segment_1 = SegmentFactory(name="segment-1", persistent=True)
    segment_2 = SegmentFactory(name="segment-2", persistent=True)

    adapter.set_segments([segment_1, segment_2])

    adapter = adapters.SessionSegmentsAdapter(request)
    segment_1.status = segment_1.STATUS_DISABLED
    segment_1.save()
    adapter.refresh()

    assert adapter.get_segments() == [segment_2]


@pytest.mark.django_db
def test_add_page_visit(rf, site):
    request = rf.get("/")

    adapter = adapters.SessionSegmentsAdapter(request)
    adapter.add_page_visit(site.root_page)

    assert request.session["visit_count"][0]["count"] == 1

    adapter.add_page_visit(site.root_page)
    assert request.session["visit_count"][0]["count"] == 2

    assert adapter.get_visit_count() == 2


@pytest.mark.django_db
def test_update_visit_count(rf, site):
    request = rf.get("/")

    adapter = adapters.SessionSegmentsAdapter(request)

    segment_1 = SegmentFactory(name="segment-1", persistent=True, visit_count=0)
    segment_2 = SegmentFactory(name="segment-2", persistent=True, visit_count=0)

    adapter.set_segments([segment_1, segment_2])
    adapter.update_visit_count()

    segment_1.refresh_from_db()
    segment_2.refresh_from_db()

    assert segment_1.visit_count == 1
    assert segment_2.visit_count == 1


@pytest.mark.django_db
def test_update_visit_count_deleted_segment(rf, site):
    request = rf.get("/")

    adapter = adapters.SessionSegmentsAdapter(request)

    segment_1 = SegmentFactory(name="segment-1", persistent=True, visit_count=0)
    segment_2 = SegmentFactory(name="segment-2", persistent=True, visit_count=0)

    adapter.set_segments([segment_1, segment_2])
    segment_2.delete()
    adapter.update_visit_count()
