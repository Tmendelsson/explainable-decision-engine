"""Unit tests for app/services/rule_engine.py"""
from types import SimpleNamespace

import pytest

from app.services.rule_engine import evaluate_rules


def _rule(name, field, operator, value, action, weight=10.0, priority=0):
    """Helper: create a minimal rule object accepted by evaluate_rules."""
    return SimpleNamespace(
        name=name,
        field=field,
        operator=operator,
        value=value,
        action=action,
        weight=weight,
        priority=priority,
    )


class TestEvaluateRules:
    # ------------------------------------------------------------------
    # Basic deny rules
    # ------------------------------------------------------------------

    def test_deny_rule_triggered(self):
        rules = [_rule("LOW_INCOME", "monthly_income", "lt", 1500, "deny")]
        payload = {"monthly_income": 1000, "age": 30, "credit_score": 600}
        matched_deny, matched_flag, penalty = evaluate_rules(payload, rules)
        assert "LOW_INCOME" in matched_deny
        assert matched_flag == []
        assert penalty == 0.0

    def test_deny_rule_not_triggered(self):
        rules = [_rule("LOW_INCOME", "monthly_income", "lt", 1500, "deny")]
        payload = {"monthly_income": 2000, "age": 30, "credit_score": 600}
        matched_deny, matched_flag, penalty = evaluate_rules(payload, rules)
        assert matched_deny == []

    # ------------------------------------------------------------------
    # Flag rules and penalty accumulation
    # ------------------------------------------------------------------

    def test_flag_rule_accumulates_penalty(self):
        rules = [
            _rule("LOW_SCORE", "credit_score", "lt", 500, "flag", weight=20.0),
            _rule("YOUNG_AGE", "age", "lt", 25, "flag", weight=15.0),
        ]
        payload = {"monthly_income": 3000, "age": 22, "credit_score": 400}
        matched_deny, matched_flag, penalty = evaluate_rules(payload, rules)
        assert "LOW_SCORE" in matched_flag
        assert "YOUNG_AGE" in matched_flag
        assert penalty == 35.0

    def test_only_matched_flag_rules_add_penalty(self):
        rules = [_rule("LOW_SCORE", "credit_score", "lt", 500, "flag", weight=20.0)]
        payload = {"monthly_income": 3000, "age": 30, "credit_score": 700}
        _, _, penalty = evaluate_rules(payload, rules)
        assert penalty == 0.0

    # ------------------------------------------------------------------
    # Operator coverage
    # ------------------------------------------------------------------

    def test_operator_gt(self):
        rules = [_rule("VERY_HIGH_INCOME", "monthly_income", "gt", 50000, "deny")]
        payload = {"monthly_income": 60000}
        matched_deny, _, _ = evaluate_rules(payload, rules)
        assert "VERY_HIGH_INCOME" in matched_deny

    def test_operator_gte_exact(self):
        rules = [_rule("INCOME_GTE", "monthly_income", "gte", 1000, "flag", weight=5.0)]
        payload = {"monthly_income": 1000}
        _, matched_flag, _ = evaluate_rules(payload, rules)
        assert "INCOME_GTE" in matched_flag

    def test_operator_lte_exact(self):
        rules = [_rule("INCOME_LTE", "monthly_income", "lte", 2000, "flag", weight=5.0)]
        payload = {"monthly_income": 2000}
        _, matched_flag, _ = evaluate_rules(payload, rules)
        assert "INCOME_LTE" in matched_flag

    def test_operator_eq(self):
        rules = [_rule("EXACT_AGE", "age", "eq", 18, "deny")]
        payload = {"age": 18}
        matched_deny, _, _ = evaluate_rules(payload, rules)
        assert "EXACT_AGE" in matched_deny

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_missing_field_is_skipped(self):
        rules = [_rule("LOW_INCOME", "monthly_income", "lt", 1500, "deny")]
        payload = {"age": 30}  # monthly_income missing
        matched_deny, matched_flag, penalty = evaluate_rules(payload, rules)
        assert matched_deny == []
        assert matched_flag == []

    def test_none_field_value_is_skipped(self):
        rules = [_rule("LOW_SCORE", "credit_score", "lt", 500, "flag")]
        payload = {"monthly_income": 2000, "age": 30, "credit_score": None}
        _, matched_flag, _ = evaluate_rules(payload, rules)
        assert matched_flag == []

    def test_invalid_operator_is_skipped(self):
        rules = [_rule("WEIRD_RULE", "monthly_income", "INVALID_OP", 1000, "deny")]
        payload = {"monthly_income": 500}
        matched_deny, _, _ = evaluate_rules(payload, rules)
        assert matched_deny == []

    def test_empty_rules_returns_empty(self):
        payload = {"monthly_income": 1000, "age": 25, "credit_score": 400}
        matched_deny, matched_flag, penalty = evaluate_rules(payload, [])
        assert matched_deny == []
        assert matched_flag == []
        assert penalty == 0.0

    # ------------------------------------------------------------------
    # Priority ordering
    # ------------------------------------------------------------------

    def test_higher_priority_rule_evaluated_first(self):
        """Verify sorted order — result should be deterministic regardless of input order."""
        rules = [
            _rule("LOW_PRIO", "monthly_income", "lt", 2000, "flag", weight=5.0, priority=1),
            _rule("HIGH_PRIO", "monthly_income", "lt", 2000, "deny", priority=10),
        ]
        payload = {"monthly_income": 1000}
        matched_deny, matched_flag, _ = evaluate_rules(payload, rules)
        # Both match; HIGH_PRIO (deny) must appear
        assert "HIGH_PRIO" in matched_deny
        assert "LOW_PRIO" in matched_flag
