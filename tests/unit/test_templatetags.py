from __future__ import absolute_import, unicode_literals

import time

import pytest
from django.template import TemplateSyntaxError
from wagtail_factories import SiteFactory

from tests.factories.segment import SegmentFactory
from tests.factories.rule import TimeRuleFactory
from tests.utils import render_template, add_session_to_request


@pytest.mark.django_db
def test_segment_template_block(rf):
    site = SiteFactory(is_default_site=True)
    segment = SegmentFactory(name='test')

    request = rf.get('/')

    add_session_to_request(request)

    request.session['segments'] = [{
        "encoded_name": 'test',
        "id": 1,
        "timestamp": int(time.time()),
        "persistent": False
    }]

    content = render_template("""
        {% load wagtail_personalisation_tags %}
        {% segment name='test' %}Test{% endsegment %}
    """, request=request).strip()

    assert content == "Test"

    content = render_template("""
        {% load wagtail_personalisation_tags %}
        {% segment name='test2' %}Test{% endsegment %}
    """, request=request).strip()

    assert content == ""

    with pytest.raises(TemplateSyntaxError):
        content = render_template("""
            {% load wagtail_personalisation_tags %}
            {% segment wrongname='test2' %}Test{% endsegment %}
        """, request=request).strip()
