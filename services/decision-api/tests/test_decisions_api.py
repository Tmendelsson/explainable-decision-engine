"""Integration tests for /api/v1/decisions endpoints."""
import pytest
from httpx import AsyncClient

VALID_PAYLOAD = {
    "cpf": "123.456.789-00",
    "product": "credit_card",
    "monthly_income": 5000.0,
    "age": 30,
    "credit_score": 650,
}

DENY_RULE = {
    "name": "LOW_INCOME_DENY",
    "description": "Renda mensal muito baixa",
    "field": "monthly_income",
    "operator": "lt",
    "value": 1000.0,
    "action": "deny",
    "weight": 0.0,
    "priority": 10,
    "is_active": True,
    "product_type": None,
}

FLAG_RULE = {
    "name": "MEDIUM_INCOME_FLAG",
    "description": "Renda média, penalidade leve",
    "field": "monthly_income",
    "operator": "lt",
    "value": 3000.0,
    "action": "flag",
    "weight": 40.0,
    "priority": 5,
    "is_active": True,
    "product_type": None,
}


class TestCreateDecision:
    async def test_approve_when_no_rules(self, client: AsyncClient):
        resp = await client.post("/api/v1/decisions/", json=VALID_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["decision"] == "approve"
        assert data["risk_score"] == 100.0
        assert data["matched_rules"] == []
        assert "transaction_id" in data

    async def test_deny_when_deny_rule_matches(self, client: AsyncClient):
        await client.post("/api/v1/rules/", json=DENY_RULE)
        payload = {**VALID_PAYLOAD, "monthly_income": 500.0}
        resp = await client.post("/api/v1/decisions/", json=payload)
        assert resp.status_code == 201
        assert resp.json()["decision"] == "deny"
        assert "LOW_INCOME_DENY" in resp.json()["matched_rules"]

    async def test_flag_rule_reduces_score(self, client: AsyncClient):
        await client.post("/api/v1/rules/", json=FLAG_RULE)
        payload = {**VALID_PAYLOAD, "monthly_income": 2000.0}
        resp = await client.post("/api/v1/decisions/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["risk_score"] == 60.0  # 100 - 40
        assert "MEDIUM_INCOME_FLAG" in data["matched_rules"]

    async def test_manual_review_on_medium_score(self, client: AsyncClient):
        """50 <= score < 70 → manual_review"""
        await client.post("/api/v1/rules/", json=FLAG_RULE)
        # weight=40 → score=60 → manual_review
        payload = {**VALID_PAYLOAD, "monthly_income": 2000.0}
        resp = await client.post("/api/v1/decisions/", json=payload)
        assert resp.json()["decision"] == "manual_review"

    async def test_deny_on_low_score(self, client: AsyncClient):
        """score < 50 → deny even without explicit deny rule"""
        heavy_flag = {**FLAG_RULE, "name": "HEAVY_PENALTY", "weight": 60.0}
        await client.post("/api/v1/rules/", json=heavy_flag)
        payload = {**VALID_PAYLOAD, "monthly_income": 2000.0}
        resp = await client.post("/api/v1/decisions/", json=payload)
        assert resp.json()["decision"] == "deny"
        assert resp.json()["risk_score"] == 40.0  # 100 - 60

    async def test_product_specific_rule_not_applied_to_other_product(self, client: AsyncClient):
        rule = {**DENY_RULE, "name": "PRODUCT_SPECIFIC", "value": 99999.0, "product_type": "personal_loan"}
        await client.post("/api/v1/rules/", json=rule)
        resp = await client.post("/api/v1/decisions/", json=VALID_PAYLOAD)  # product=credit_card
        assert resp.json()["decision"] == "approve"

    async def test_missing_required_field_returns_422(self, client: AsyncClient):
        resp = await client.post("/api/v1/decisions/", json={"cpf": "123"})
        assert resp.status_code == 422

    async def test_invalid_cpf_too_short_returns_422(self, client: AsyncClient):
        bad = {**VALID_PAYLOAD, "cpf": "12345"}
        resp = await client.post("/api/v1/decisions/", json=bad)
        assert resp.status_code == 422

    async def test_invalid_age_zero_returns_422(self, client: AsyncClient):
        bad = {**VALID_PAYLOAD, "age": 0}
        resp = await client.post("/api/v1/decisions/", json=bad)
        assert resp.status_code == 422

    async def test_negative_income_returns_422(self, client: AsyncClient):
        bad = {**VALID_PAYLOAD, "monthly_income": -100.0}
        resp = await client.post("/api/v1/decisions/", json=bad)
        assert resp.status_code == 422


class TestGetDecision:
    async def test_get_existing_decision(self, client: AsyncClient):
        created = (await client.post("/api/v1/decisions/", json=VALID_PAYLOAD)).json()
        resp = await client.get(f"/api/v1/decisions/{created['transaction_id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["transaction_id"] == created["transaction_id"]
        assert data["product"] == VALID_PAYLOAD["product"]

    async def test_get_nonexistent_decision_returns_404(self, client: AsyncClient):
        resp = await client.get("/api/v1/decisions/nonexistent-uuid")
        assert resp.status_code == 404

    async def test_cpf_present_in_detail_response(self, client: AsyncClient):
        created = (await client.post("/api/v1/decisions/", json=VALID_PAYLOAD)).json()
        resp = await client.get(f"/api/v1/decisions/{created['transaction_id']}")
        assert resp.json()["cpf"] == VALID_PAYLOAD["cpf"]
