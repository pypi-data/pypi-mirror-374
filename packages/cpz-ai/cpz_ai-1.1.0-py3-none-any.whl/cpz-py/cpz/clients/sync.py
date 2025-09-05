from __future__ import annotations

from ..common.cpz_ai import CPZAIClient as SupabaseClient
from ..execution.models import Account, Order, OrderReplaceRequest, OrderSubmitRequest, Position
from ..execution.router import BrokerRouter
from .base import BaseClient


class _ExecutionNamespace:
    def __init__(self, router: BrokerRouter) -> None:
        self.router = router

    def use_broker(self, name: str, **kwargs: object) -> None:
        self.router.use_broker(name, **kwargs)

    def get_account(self) -> Account:
        return self.router.get_account()

    def get_positions(self) -> list[Position]:
        return self.router.get_positions()

    def submit_order(self, req: OrderSubmitRequest) -> Order:
        return self.router.submit_order(req)

    def get_order(self, order_id: str) -> Order:
        return self.router.get_order(order_id)

    def cancel_order(self, order_id: str) -> Order:
        return self.router.cancel_order(order_id)

    def replace_order(self, order_id: str, req: OrderReplaceRequest) -> Order:
        return self.router.replace_order(order_id, req)

    # Convenience: one-call order placement with CPZ-managed broker creds
    def order(
        self,
        *,
        symbol: str,
        qty: float,
        side: str = "buy",
        order_type: str = "market",
        time_in_force: str = "DAY",
        limit_price: float | None = None,
        broker: str = "alpaca",
        env: str = "paper",
        strategy_id: str,
    ) -> Order:
        from ..execution.enums import OrderSide, OrderType, TimeInForce
        # Ensure a broker is selected; adapter will fetch creds from CPZ AI
        self.router.use_broker(broker, env=env)

        side_enum = OrderSide.BUY if str(side).lower() == "buy" else OrderSide.SELL
        type_enum = OrderType.MARKET if str(order_type).lower() == "market" else OrderType.LIMIT
        tif_enum = TimeInForce(str(time_in_force).upper())

        req = OrderSubmitRequest(
            symbol=symbol,
            side=side_enum,
            qty=qty,
            type=type_enum,
            time_in_force=tif_enum,
            limit_price=limit_price,
            strategy_id=strategy_id,
        )
        return self.router.submit_order(req)


class _PlatformNamespace:
    def __init__(self) -> None:
        self._sb: SupabaseClient | None = None

    def configure(
        self, *, url: str | None = None, anon: str | None = None, service: str | None = None
    ) -> None:
        if url and anon:
            self._sb = SupabaseClient(url=url, anon_key=anon, service_key=service)
        else:
            self._sb = SupabaseClient.from_env()

    def _require(self) -> SupabaseClient:
        if self._sb is None:
            self._sb = SupabaseClient.from_env()
        return self._sb

    def health(self) -> bool:
        return self._require().health()

    def echo(self) -> dict[str, object]:
        return self._require().echo()

    def list_tables(self) -> list[str]:
        return self._require().list_tables()


class CPZClient(BaseClient):
    def __init__(self) -> None:
        super().__init__()
        self.execution = _ExecutionNamespace(BrokerRouter.default())
        self.platform = _PlatformNamespace()

    @property
    def router(self) -> BrokerRouter:
        return self.execution.router
