from __future__ import absolute_import, unicode_literals

import time

import pytest
from django.template import TemplateSyntaxError

from tests.factories.segment import SegmentFactory
from tests.utils import render_template


@pytest.mark.django_db
def test_segment_template_block(rf, site):
    SegmentFactory(name="test", persistent=True)

    request = rf.get("/")

    request.session["segments"] = [
        {
            "encoded_name": "test",
            "id": 1,
            "timestamp": int(time.time()),
            "persistent": True,
        }
    ]

    content = render_template(
        """
        {% load wagtail_personalisation_tags %}
        {% segment name='test' %}Test{% endsegment %}
    """,
        request=request,
    ).strip()

    assert content == "Test"

    content = render_template(
        """
        {% load wagtail_personalisation_tags %}
        {% segment name='test2' %}Test{% endsegment %}
    """,
        request=request,
    ).strip()

    assert content == ""

    with pytest.raises(TemplateSyntaxError):
        content = render_template(
            """
            {% load wagtail_personalisation_tags %}
            {% segment wrongname='test2' %}Test{% endsegment %}
        """,
            request=request,
        ).strip()
