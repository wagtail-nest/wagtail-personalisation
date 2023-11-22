import pytest

from tests.factories.rule import QueryRuleFactory
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
def test_request_query_rule(client, site):
    segment = SegmentFactory(name="Query")
    QueryRuleFactory(
        parameter="query",
        value="value",
        segment=segment,
    )

    response = client.get("/?query=value")
    assert response.status_code == 200

    assert any(item["encoded_name"] == "query" for item in client.session["segments"])


@pytest.mark.django_db
def test_request_only_one_query_rule(client, site):
    segment = SegmentFactory(name="Query")
    QueryRuleFactory(parameter="query", value="value", segment=segment)

    response = client.get("/?test=test&query=value")
    assert response.status_code == 200
    assert any(item["encoded_name"] == "query" for item in client.session["segments"])


@pytest.mark.django_db
def test_request_multiple_queries(client, site):
    segment = SegmentFactory(name="Multiple queries")
    QueryRuleFactory(parameter="test", value="test", segment=segment)

    QueryRuleFactory(
        parameter="query",
        value="value",
        segment=segment,
    )

    response = client.get("/?test=test&query=value")
    assert response.status_code == 200
    assert any(
        item["encoded_name"] == "multiple-queries"
        for item in client.session["segments"]
    )


@pytest.mark.django_db
def test_request_persistent_segmenting(client, site):
    segment = SegmentFactory(name="Persistent", persistent=True)
    QueryRuleFactory(parameter="test", value="test", segment=segment)

    response = client.get("/?test=test")
    assert response.status_code == 200

    assert any(
        item["encoded_name"] == "persistent" for item in client.session["segments"]
    )

    response = client.get("/")
    assert response.status_code == 200
    assert any(
        item["encoded_name"] == "persistent" for item in client.session["segments"]
    )


@pytest.mark.django_db
def test_request_non_persistent_segmenting(client, site):
    segment = SegmentFactory(name="Non Persistent")
    QueryRuleFactory(parameter="test", value="test", segment=segment)

    response = client.get("/?test=test")
    assert response.status_code == 200
    assert any(
        item["encoded_name"] == "non-persistent" for item in client.session["segments"]
    )

    response = client.get("/")
    assert response.status_code == 200

    assert not any(
        item["encoded_name"] == "non-persistent" for item in client.session["segments"]
    )


@pytest.mark.django_db
def test_request_match_any_segmenting(client, site):
    segment = SegmentFactory(name="Match any", match_any=True)
    QueryRuleFactory(
        parameter="test",
        value="test",
        segment=segment,
    )
    QueryRuleFactory(parameter="test2", value="test2", segment=segment)

    response = client.get("/?test=test")
    assert response.status_code == 200

    assert any(
        item["encoded_name"] == "match-any" for item in client.session["segments"]
    )
