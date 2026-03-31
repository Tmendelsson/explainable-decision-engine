"""
RabbitMQ Consumer — Rule Engine Service

Consome eventos DecisionRequested, avalia regras e publica RulesEvaluated.
"""
import json
import logging
import time
from datetime import datetime, timezone

from aio_pika import IncomingMessage, connect_robust
from aio_pika.abc import AbstractRobustConnection
from sqlalchemy import select

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.messaging.publisher import publish_rules_evaluated
from app.models.rule import Rule
from app.services.evaluator import (
    calculate_risk_score,
    determine_decision,
    evaluate_rules,
)

logger = logging.getLogger(__name__)
settings = get_settings()

_connection: AbstractRobustConnection | None = None


async def get_connection() -> AbstractRobustConnection:
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await connect_robust(settings.rabbitmq_url)
    return _connection


async def close_connection() -> None:
    global _connection
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None


async def _handle_decision_requested(message: IncomingMessage) -> None:
    async with message.process(requeue=True):
        try:
            body = json.loads(message.body)
            transaction_id = body.get("transaction_id", "unknown")
            correlation_id = body.get("correlation_id", "unknown")
            payload = body.get("payload", {})
            enriched = body.get("enriched_data") or {}

            logger.info(
                "Received DecisionRequested transaction_id=%s", transaction_id
            )

            # Merge enriched credit_score into payload when available
            eval_payload = {**payload}
            if enriched.get("credit_score") is not None:
                eval_payload["credit_score"] = enriched["credit_score"]

            product = payload.get("product")

            async with AsyncSessionLocal() as db:
                stmt = select(Rule).where(Rule.is_active == True)
                result = await db.execute(stmt)
                all_rules = result.scalars().all()

            applicable = [
                r for r in all_rules
                if r.product_type is None or r.product_type == product
            ]

            t0 = time.monotonic()
            matched_deny, matched_flag, total_penalty = evaluate_rules(eval_payload, applicable)
            risk_score = calculate_risk_score(total_penalty)
            base_decision = determine_decision(matched_deny, risk_score)
            latency_ms = int((time.monotonic() - t0) * 1000)

            all_matched = matched_deny + matched_flag
            rules_snapshot = [
                {
                    "name": r.name,
                    "field": r.field,
                    "operator": r.operator,
                    "value": r.value,
                    "action": r.action,
                    "weight": r.weight,
                    "version": r.version,
                }
                for r in applicable
            ]

            await publish_rules_evaluated(
                transaction_id=transaction_id,
                correlation_id=correlation_id,
                base_decision=base_decision,
                risk_score=risk_score,
                matched_rules=all_matched,
                rules_snapshot=rules_snapshot,
                latency_ms=latency_ms,
            )

            logger.info(
                "RulesEvaluated published transaction_id=%s decision=%s score=%.2f latency_ms=%d",
                transaction_id,
                base_decision,
                risk_score,
                latency_ms,
            )

        except Exception as exc:
            logger.exception(
                "Failed processing DecisionRequested: %s", exc
            )
            raise


async def start_consumer() -> None:
    """Inicia o consumer e fica escutando a fila indefinidamente."""
    conn = await get_connection()
    channel = await conn.channel()
    await channel.set_qos(prefetch_count=10)

    exchange = await channel.declare_exchange(
        settings.exchange_name, durable=True
    )
    queue = await channel.declare_queue(settings.queue_name, durable=True)
    await queue.bind(
        exchange, routing_key=settings.decision_requested_routing_key
    )

    await queue.consume(_handle_decision_requested)
    logger.info(
        "Consumer started: queue=%s routing_key=%s",
        settings.queue_name,
        settings.decision_requested_routing_key,
    )
