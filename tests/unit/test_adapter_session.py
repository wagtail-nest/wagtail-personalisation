import pytest

from wagtail_personalisation import adapters
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
def test_get_segments(rf, monkeypatch):
    request = rf.get('/')

    adapter = adapters.SessionSegmentsAdapter(request)

    segment_1 = SegmentFactory(name='segment-1', persistent=True)
    segment_2 = SegmentFactory(name='segment-2', persistent=True)

    adapter.set_segments([segment_1, segment_2])
    assert len(request.session['segments']) == 2

    segments = adapter.get_segments()
    assert segments == [segment_1, segment_2]


@pytest.mark.django_db
def test_get_segment_by_id(rf, monkeypatch):
    request = rf.get('/')

    adapter = adapters.SessionSegmentsAdapter(request)

    segment_1 = SegmentFactory(name='segment-1', persistent=True)
    segment_2 = SegmentFactory(name='segment-2', persistent=True)

    adapter.set_segments([segment_1, segment_2])

    segment_x = adapter.get_segment_by_id(segment_2.pk)
    assert segment_x == segment_2


@pytest.mark.django_db
def test_refresh_removes_disabled(rf, monkeypatch):
    request = rf.get('/')

    adapter = adapters.SessionSegmentsAdapter(request)

    segment_1 = SegmentFactory(name='segment-1', persistent=True)
    segment_2 = SegmentFactory(name='segment-2', persistent=True)

    adapter.set_segments([segment_1, segment_2])

    adapter = adapters.SessionSegmentsAdapter(request)
    segment_1.status = segment_1.STATUS_DISABLED
    segment_1.save()
    adapter.refresh()

    assert adapter.get_segments() == [segment_2]
