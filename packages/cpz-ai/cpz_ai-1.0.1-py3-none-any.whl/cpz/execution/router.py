from __future__ import annotations

import os
from datetime import datetime
from typing import AsyncIterator, Callable, Dict, Iterable, Optional

from ..common.cpz_ai import CPZAIClient
from ..common.errors import BrokerNotRegistered
from .interfaces import BrokerAdapter
from .models import Account, Order, OrderReplaceRequest, OrderSubmitRequest, Position, Quote, Bar

BROKER_ALPACA = "alpaca"
BROKER_CPZ_NATIVE = "cpz-native"


class BrokerRouter:
    _registry: Dict[str, Callable[..., BrokerAdapter]] = {}

    def __init__(self, cpz_client: Optional[CPZAIClient] = None) -> None:
        self._active: Optional[BrokerAdapter] = None
        self._broker: Optional[str] = None
        self._environment: Optional[str] = None
        self._account_id: Optional[str] = None
        self._cpz_client = cpz_client or CPZAIClient.from_env()

    @classmethod
    def register(cls, name: str, factory: Callable[..., BrokerAdapter]) -> None:
        cls._registry[name] = factory

    def list_brokers(self) -> list[str]:
        return list(self._registry.keys())

    @classmethod
    def default(cls) -> "BrokerRouter":
        # Always register CPZ native (brokerless) adapter
        try:
            from .cpz_native_adapter import CPZNativeAdapter
            cls.register(BROKER_CPZ_NATIVE, CPZNativeAdapter.create)
        except Exception:
            pass

        # Register Alpaca if available
        if BROKER_ALPACA not in cls._registry:
            try:
                from .alpaca.adapter import AlpacaAdapter
                cls.register(BROKER_ALPACA, AlpacaAdapter.create)
            except Exception:
                pass
        return cls()
    
    def with_cpz_client(self, cpz_client: CPZAIClient) -> "BrokerRouter":
        """Update this router instance with a specific CPZ AI client."""
        self._cpz_client = cpz_client
        return self

    def use_broker(self, name: str, environment: str = "paper", account_id: Optional[str] = None) -> None:
        """Configure broker for execution. Credentials are resolved from CPZ AI."""
        if name not in self._registry:
            raise BrokerNotRegistered(name)
        
        # Validate environment
        if environment not in ("paper", "live"):
            raise ValueError(f"Invalid environment: {environment}. Must be 'paper' or 'live'")
        
        self._broker = name
        self._environment = environment
        self._account_id = account_id
        self._active = None  # Will be initialized when needed with credentials

    def _resolve_credentials(self) -> Dict[str, str]:
        """Resolve trading credentials from CPZ AI for the configured broker."""
        if not self._broker or not self._environment:
            raise ValueError("Broker and environment must be configured first. Call use_broker().")
        
        credentials = self._cpz_client.get_trading_credentials(
            broker=self._broker,
            environment=self._environment,
            account_id=self._account_id
        )
        
        if not credentials:
            raise ValueError(f"No active trading credentials found for {self._broker} in {self._environment} environment")
        
        return {
            "api_key_id": credentials["api_key"],
            "api_secret_key": credentials["api_secret"],
            "env": self._environment,
            "account_id": credentials.get("account_id")
        }

    def _require_active(self) -> BrokerAdapter:
        if self._active is None:
            if not self._broker:
                raise ValueError("No broker configured. Call use_broker() first.")
            
            # Resolve credentials and create adapter
            creds = self._resolve_credentials()
            factory = self._registry[self._broker]
            self._active = factory(**creds)
        
        return self._active

    # --------------------- Execution ---------------------
    def get_account(self) -> Account:
        return self._require_active().get_account()

    def get_positions(self) -> list[Position]:
        return self._require_active().get_positions()

    def submit_order(self, req: OrderSubmitRequest) -> Order:
        """Submit order through CPZ AI with full tracking and broker execution."""
        if not self._broker or not self._environment:
            raise ValueError("Broker and environment must be configured first. Call use_broker().")
        
        # Step 1: Create order record in CPZ AI 
        cpz_order_data = {
            "client_order_id": req.client_order_id,
            "broker": self._broker,
            "environment": self._environment,
            "account_id": self._account_id,
            "strategy_id": req.strategy_id,
            "symbol": req.symbol,
            "side": req.side.value,
            "qty": req.qty,
            "order_type": req.type.value,
            "time_in_force": req.time_in_force.value,
            "limit_price": req.limit_price,
            "stop_price": req.stop_price,
            "status": "pending_broker",
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        # Check for existing order by client_order_id (idempotency)
        existing_order = self._cpz_client.get_order_by_client_id(req.client_order_id)
        if existing_order:
            if existing_order["status"] in ("placed", "filled"):
                # Order already successfully placed, return it
                return self._map_cpz_order_to_order(existing_order)
            elif existing_order["status"] == "failed":
                raise ValueError(f"Order {req.client_order_id} previously failed: {existing_order.get('error_message', 'Unknown error')}")
        
        if not existing_order:
            # Create new order in CPZ AI
            cpz_order = self._cpz_client.create_order(cpz_order_data)
            if not cpz_order:
                raise ValueError("Failed to create order in CPZ AI")
        else:
            cpz_order = existing_order
        
        try:
            # Step 2: Execute order at broker
            broker_adapter = self._require_active()
            broker_order = broker_adapter.submit_order(req)
            
            # Step 3: Update CPZ order with success
            update_data = {
                "status": "placed",
                "broker_order_id": broker_order.id,
                "placed_at": datetime.utcnow().isoformat()
            }
            self._cpz_client.update_order(cpz_order["id"], update_data)
            
            # Return the broker order (enhanced with CPZ info)
            broker_order.id = cpz_order["id"]  # Use CPZ order ID as primary
            return broker_order
            
        except Exception as e:
            # Step 3b: Update CPZ order with failure
            update_data = {
                "status": "failed",
                "error_message": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
            self._cpz_client.update_order(cpz_order["id"], update_data)
            raise ValueError(f"Order execution failed: {e}")

    def _map_cpz_order_to_order(self, cpz_order: dict) -> Order:
        """Convert CPZ order to Order model."""
        return Order(
            id=cpz_order["id"],
            symbol=cpz_order["symbol"],
            side=cpz_order["side"],
            qty=cpz_order["qty"],
            type=cpz_order["order_type"],
            time_in_force=cpz_order["time_in_force"],
            status=cpz_order["status"],
            created_at=datetime.fromisoformat(cpz_order["submitted_at"])
        )

    def get_order(self, order_id: str) -> Order:
        return self._require_active().get_order(order_id)

    def cancel_order(self, order_id: str) -> Order:
        return self._require_active().cancel_order(order_id)

    def replace_order(self, order_id: str, req: OrderReplaceRequest) -> Order:
        return self._require_active().replace_order(order_id, req)

    def stream_quotes(self, symbols: Iterable[str]) -> AsyncIterator[Quote]:
        active = self._require_active()
        return active.stream_quotes(symbols)

    # ----------------------- Data ------------------------
    def get_quotes(self, symbols: list[str]) -> list[Quote]:
        return self._require_active().get_quotes(symbols)

    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> list[Bar]:
        return self._require_active().get_historical_data(symbol, timeframe, limit, start, end)
