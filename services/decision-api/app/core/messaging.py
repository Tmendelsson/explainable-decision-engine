"""
Messaging Layer — Decision API MVP 2

Responsabilidades:
  - Publicar DecisionRequested no exchange decision.events
  - Consumir RulesEvaluated e notificar o orchestrator via asyncio.Event
"""
import asyncio
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

# Mapa de transaction_id → asyncio.Event + resultado
_pending: dict[str, tuple[asyncio.Event, dict | None]] = {}


async def _get_connection() -> AbstractRobustConnection:
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await connect_robust(settings.rabbitmq_url)
    return _connection


async def close_messaging() -> None:
    global _connection
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None


# ---------------------------------------------------------------------------
# Publisher
# ---------------------------------------------------------------------------


async def publish_decision_requested(
    transaction_id: str,
    correlation_id: str,
    payload: dict[str, Any],
    enriched_data: dict[str, Any] | None = None,
) -> None:
    conn = await _get_connection()
    channel = await conn.channel()
    exchange = await channel.declare_exchange(settings.exchange_name, durable=True)

    body = {
        "event_type": "DecisionRequested",
        "transaction_id": transaction_id,
        "correlation_id": correlation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service_name": "decision-api",
        "service_version": settings.app_version,
        "payload": payload,
        "enriched_data": enriched_data,
    }

    await exchange.publish(
        Message(
            body=json.dumps(body).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        ),
        routing_key=settings.decision_requested_routing_key,
    )
    logger.debug("Published DecisionRequested transaction_id=%s", transaction_id)


# ---------------------------------------------------------------------------
# Consumer (RulesEvaluated)
# ---------------------------------------------------------------------------


async def _handle_rules_evaluated(message) -> None:
    async with message.process():
        try:
            body = json.loads(message.body)
            tid = body.get("transaction_id")
            if tid and tid in _pending:
                event, _ = _pending[tid]
                _pending[tid] = (event, body)
                event.set()
                logger.debug("RulesEvaluated received transaction_id=%s", tid)
            else:
                logger.debug(
                    "RulesEvaluated for unknown transaction_id=%s (late/orphan)", tid
                )
        except Exception as exc:
            logger.exception("Error processing RulesEvaluated: %s", exc)


async def start_consumer() -> None:
    """
    Inicia o consumer de RulesEvaluated.
    Deve ser chamado no lifespan do FastAPI.
    """
    conn = await _get_connection()
    channel = await conn.channel()
    await channel.set_qos(prefetch_count=50)

    exchange = await channel.declare_exchange(settings.exchange_name, durable=True)
    queue = await channel.declare_queue(
        settings.rules_evaluated_queue, durable=True
    )
    await queue.bind(
        exchange, routing_key=settings.rules_evaluated_routing_key
    )
    await queue.consume(_handle_rules_evaluated)
    logger.info(
        "RulesEvaluated consumer started queue=%s", settings.rules_evaluated_queue
    )


# ---------------------------------------------------------------------------
# Request/reply helper
# ---------------------------------------------------------------------------


async def wait_for_rules_evaluated(
    transaction_id: str, timeout: float
) -> dict[str, Any] | None:
    """
    Registra uma espera e retorna o payload de RulesEvaluated quando chegar,
    ou None se estourar o timeout.
    """
    event = asyncio.Event()
    _pending[transaction_id] = (event, None)
    try:
        await asyncio.wait_for(event.wait(), timeout=timeout)
        _, result = _pending[transaction_id]
        return result
    except asyncio.TimeoutError:
        logger.warning(
            "Timeout waiting for RulesEvaluated transaction_id=%s", transaction_id
        )
        return None
    finally:
        _pending.pop(transaction_id, None)
