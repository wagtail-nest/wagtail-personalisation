import pytest

from tests.factories.rule import ReferralRuleFactory
from tests.factories.segment import SegmentFactory


@pytest.mark.django_db
def test_referral_rule_create():
    segment = SegmentFactory(name="Referral")
    referral_rule = ReferralRuleFactory(regex_string="test.test", segment=segment)

    assert referral_rule.regex_string == "test.test"
