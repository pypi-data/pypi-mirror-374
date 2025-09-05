from __future__ import annotations

import os
from typing import AsyncIterator, Callable, Dict, Iterable, Optional

from ..common.errors import BrokerNotRegistered
from .interfaces import BrokerAdapter
from .models import Account, Order, OrderReplaceRequest, OrderSubmitRequest, Position, Quote

BROKER_ALPACA = "alpaca"


class BrokerRouter:
    _registry: Dict[str, Callable[..., BrokerAdapter]] = {}

    def __init__(self) -> None:
        self._active: Optional[BrokerAdapter] = None
        self._active_name: Optional[str] = None
        self._active_kwargs: Dict[str, object] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[..., BrokerAdapter]) -> None:
        cls._registry[name] = factory

    def list_brokers(self) -> list[str]:
        return list(self._registry.keys())

    @classmethod
    def default(cls) -> "BrokerRouter":
        if BROKER_ALPACA not in cls._registry:
            try:
                from .alpaca.adapter import AlpacaAdapter

                cls.register(BROKER_ALPACA, AlpacaAdapter.create)
            except Exception:
                pass
        return cls()

    def use_broker(self, name: str, **kwargs: object) -> None:
        if name not in self._registry:
            raise BrokerNotRegistered(name)
        factory = self._registry[name]
        self._active = factory(**kwargs)
        self._active_name = name
        self._active_kwargs = dict(kwargs)

    def _require_active(self) -> BrokerAdapter:
        if self._active is None:
            if len(self._registry) == 1:
                _name, factory = next(iter(self._registry.items()))
                self._active = factory()
                return self._active
            if os.getenv("ALPACA_API_KEY_ID"):
                self.use_broker(BROKER_ALPACA, env=os.getenv("ALPACA_ENV", "paper"))
            else:
                raise BrokerNotRegistered("<none>")
        assert self._active is not None
        return self._active

    def get_account(self) -> Account:
        return self._require_active().get_account()

    def get_positions(self) -> list[Position]:
        return self._require_active().get_positions()

    def submit_order(self, req: OrderSubmitRequest) -> Order:
        from ..common.cpz_ai import CPZAIClient

        broker_name = self._active_name or BROKER_ALPACA
        env = str(self._active_kwargs.get("env") or "paper")

        # 1) Create order intent (must succeed) before sending to broker
        sb = CPZAIClient.from_env()
        intent = sb.create_order_intent(
            symbol=req.symbol,
            side=req.side.value,
            qty=req.qty,
            type=req.type.value,
            time_in_force=req.time_in_force.value,
            broker=broker_name,
            env=env,
            strategy_id=getattr(req, "strategy_id", ""),
            status="pending",
        )
        if not intent or not isinstance(intent, dict) or not intent.get("id"):
            # Abort: cannot record intent
            raise RuntimeError("Failed to record order intent in CPZ orders table")

        # 2) Send to broker
        order = self._require_active().submit_order(req)

        # 3) Update order record with broker order_id and status
        try:
            sb.update_order_record(id=str(intent.get("id")), order_id=order.id, status=getattr(order, "status", None))
        except Exception:
            pass

        return order

    def get_order(self, order_id: str) -> Order:
        return self._require_active().get_order(order_id)

    def cancel_order(self, order_id: str) -> Order:
        return self._require_active().cancel_order(order_id)

    def replace_order(self, order_id: str, req: OrderReplaceRequest) -> Order:
        return self._require_active().replace_order(order_id, req)

    def stream_quotes(self, symbols: Iterable[str]) -> AsyncIterator[Quote]:
        active = self._require_active()
        return active.stream_quotes(symbols)
