import pytest


@pytest.mark.django_db
def test_request_device_segment_no_match(client, site):
    response = client.get("/regular/")
    assert response.status_code == 200
