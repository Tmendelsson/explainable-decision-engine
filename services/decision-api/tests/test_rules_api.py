"""Integration tests for /api/v1/rules endpoints."""
import pytest
from httpx import AsyncClient

VALID_RULE = {
    "name": "TEST_LOW_INCOME",
    "description": "Renda mensal abaixo do mínimo exigido",
    "field": "monthly_income",
    "operator": "lt",
    "value": 1500.0,
    "action": "deny",
    "weight": 50.0,
    "priority": 9,
    "is_active": True,
    "product_type": None,
}


class TestCreateRule:
    async def test_create_valid_rule_returns_201(self, client: AsyncClient):
        resp = await client.post("/api/v1/rules/", json=VALID_RULE)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == VALID_RULE["name"]
        assert data["operator"] == "lt"
        assert "id" in data

    async def test_create_rule_invalid_operator_returns_422(self, client: AsyncClient):
        bad = {**VALID_RULE, "name": "BAD_OP", "operator": "UNKNOWN"}
        resp = await client.post("/api/v1/rules/", json=bad)
        assert resp.status_code == 422

    async def test_create_rule_invalid_action_returns_422(self, client: AsyncClient):
        bad = {**VALID_RULE, "name": "BAD_ACT", "action": "explode"}
        resp = await client.post("/api/v1/rules/", json=bad)
        assert resp.status_code == 422

    async def test_create_rule_invalid_field_returns_422(self, client: AsyncClient):
        bad = {**VALID_RULE, "name": "BAD_FIELD", "field": "salary"}
        resp = await client.post("/api/v1/rules/", json=bad)
        assert resp.status_code == 422

    async def test_duplicate_name_returns_409(self, client: AsyncClient):
        await client.post("/api/v1/rules/", json=VALID_RULE)
        resp = await client.post("/api/v1/rules/", json=VALID_RULE)
        assert resp.status_code == 409

    async def test_missing_required_fields_returns_422(self, client: AsyncClient):
        resp = await client.post("/api/v1/rules/", json={"name": "INCOMPLETE"})
        assert resp.status_code == 422


class TestListRules:
    async def test_list_rules_empty(self, client: AsyncClient):
        resp = await client.get("/api/v1/rules/")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_rules_returns_created(self, client: AsyncClient):
        await client.post("/api/v1/rules/", json=VALID_RULE)
        resp = await client.get("/api/v1/rules/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_list_rules_pagination(self, client: AsyncClient):
        for i in range(5):
            await client.post("/api/v1/rules/", json={**VALID_RULE, "name": f"RULE_{i}"})
        resp = await client.get("/api/v1/rules/?skip=0&limit=3&active_only=false")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    async def test_list_rules_limit_max_200(self, client: AsyncClient):
        resp = await client.get("/api/v1/rules/?limit=201")
        assert resp.status_code == 422


class TestGetRule:
    async def test_get_existing_rule(self, client: AsyncClient):
        created = (await client.post("/api/v1/rules/", json=VALID_RULE)).json()
        resp = await client.get(f"/api/v1/rules/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    async def test_get_nonexistent_rule_returns_404(self, client: AsyncClient):
        resp = await client.get("/api/v1/rules/nonexistent-id")
        assert resp.status_code == 404


class TestToggleRule:
    async def test_toggle_deactivates_rule(self, client: AsyncClient):
        created = (await client.post("/api/v1/rules/", json=VALID_RULE)).json()
        resp = await client.patch(f"/api/v1/rules/{created['id']}/toggle")
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    async def test_toggle_twice_reactivates_rule(self, client: AsyncClient):
        created = (await client.post("/api/v1/rules/", json=VALID_RULE)).json()
        await client.patch(f"/api/v1/rules/{created['id']}/toggle")
        resp = await client.patch(f"/api/v1/rules/{created['id']}/toggle")
        assert resp.json()["is_active"] is True

    async def test_toggle_nonexistent_returns_404(self, client: AsyncClient):
        resp = await client.patch("/api/v1/rules/nonexistent/toggle")
        assert resp.status_code == 404
