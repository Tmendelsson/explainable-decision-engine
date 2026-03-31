"""
RabbitMQ Publisher — Rule Engine Service

Publica eventos RulesEvaluated no exchange decision.events.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any

from aio_pika import DeliveryMode, Message, connect_robust
from aio_pika.abc import AbstractRobustConnection

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_connection: AbstractRobustConnection | None = None


async def _get_connection() -> AbstractRobustConnection:
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await connect_robust(settings.rabbitmq_url)
    return _connection


async def publish_rules_evaluated(
    transaction_id: str,
    correlation_id: str,
    base_decision: str,
    risk_score: float,
    matched_rules: list[str],
    rules_snapshot: list[dict[str, Any]],
    latency_ms: int,
) -> None:
    conn = await _get_connection()
    channel = await conn.channel()

    exchange = await channel.declare_exchange(
        settings.exchange_name, durable=True
    )

    payload = {
        "event_type": "RulesEvaluated",
        "transaction_id": transaction_id,
        "correlation_id": correlation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service_name": "rule-engine-service",
        "service_version": settings.app_version,
        "base_decision": base_decision,
        "risk_score": risk_score,
        "matched_rules": matched_rules,
        "rules_version_snapshot": rules_snapshot,
        "latency_ms": latency_ms,
    }

    message = Message(
        body=json.dumps(payload).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        content_type="application/json",
    )

    await exchange.publish(
        message, routing_key=settings.rules_evaluated_routing_key
    )
    logger.debug(
        "Published RulesEvaluated transaction_id=%s routing_key=%s",
        transaction_id,
        settings.rules_evaluated_routing_key,
    )
