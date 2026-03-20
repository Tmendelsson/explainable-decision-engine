"""Unit tests for app/services/scoring.py"""
import pytest

from app.services.scoring import calculate_risk_score, determine_decision


# ---------------------------------------------------------------------------
# calculate_risk_score
# ---------------------------------------------------------------------------

class TestCalculateRiskScore:
    def test_no_penalty_returns_100(self):
        assert calculate_risk_score(0.0) == 100.0

    def test_full_penalty_returns_0(self):
        assert calculate_risk_score(100.0) == 0.0

    def test_partial_penalty(self):
        assert calculate_risk_score(30.0) == 70.0

    def test_over_penalty_clamps_to_zero(self):
        assert calculate_risk_score(150.0) == 0.0

    def test_result_is_rounded_to_two_decimals(self):
        score = calculate_risk_score(33.333)
        assert score == round(max(0.0, 100.0 - 33.333), 2)


# ---------------------------------------------------------------------------
# determine_decision
# ---------------------------------------------------------------------------

class TestDetermineDecision:
    def test_approve_when_score_above_threshold(self):
        assert determine_decision([], 80.0) == "approve"

    def test_approve_at_exact_threshold(self):
        assert determine_decision([], 70.0) == "approve"

    def test_manual_review_between_thresholds(self):
        assert determine_decision([], 60.0) == "manual_review"

    def test_manual_review_at_lower_threshold(self):
        assert determine_decision([], 50.0) == "manual_review"

    def test_deny_below_lower_threshold(self):
        assert determine_decision([], 49.9) == "deny"

    def test_deny_on_zero_score(self):
        assert determine_decision([], 0.0) == "deny"

    def test_deny_overrides_good_score(self):
        assert determine_decision(["HIGH_RISK_FLAG"], 95.0) == "deny"

    def test_deny_with_multiple_matched_deny_rules(self):
        assert determine_decision(["RULE_A", "RULE_B"], 85.0) == "deny"

    def test_custom_thresholds_approve(self):
        assert determine_decision([], 85.0, approve_threshold=80.0, manual_review_threshold=60.0) == "approve"

    def test_custom_thresholds_manual_review(self):
        assert determine_decision([], 70.0, approve_threshold=80.0, manual_review_threshold=60.0) == "manual_review"

    def test_custom_thresholds_deny(self):
        assert determine_decision([], 50.0, approve_threshold=80.0, manual_review_threshold=60.0) == "deny"
