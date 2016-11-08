import datetime

import pytest
from personalisation.models import TimeRule


@pytest.mark.django_db
def test_create_time_rule():
    time_rule = TimeRule(name='test', start_time="08:00:00", end_time="23:00:00")

    with mock.patch('TimeRule.get_current_time', return_value=datetime.time(10, 00, 00)):
        assert time_rule.test_user() is True
