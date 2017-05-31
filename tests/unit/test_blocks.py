from __future__ import absolute_import, unicode_literals

import pytest

from tests.factories.segment import SegmentFactory
from test.factories.pages import PersonalisedFieldsPageFactory
from tests.utils import render_template

@pytest.mark.django_db
def test_render_block(rf):
    SegmentFactory(name='test', persistent=True)

    request = rf.get('/')

    request.session['segments'] = [{
        "encoded_name": 'test',
        "id": 1,
        "timestamp": int(time.time()),
        "persistent": True
    }]

    PersonalisedFieldsPageFactory(body=)

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
