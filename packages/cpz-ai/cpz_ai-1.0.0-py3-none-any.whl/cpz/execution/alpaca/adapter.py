from __future__ import annotations

import os
from datetime import datetime
from types import SimpleNamespace
from typing import AsyncIterator, Iterable, List, Optional

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest, ReplaceOrderRequest

from ..enums import OrderSide, OrderType, TimeInForce
from ..interfaces import BrokerAdapter
from ..models import (
    OrderSubmitRequest,
    OrderReplaceRequest,
    Order,
    Account,
    Position,
    Quote,
    Bar,
)
from .mapping import map_order_status


def _mk_side(value: str):
    try:
        from alpaca.trading.enums import OrderSide as AlpacaSide  # type: ignore
        return AlpacaSide(value)
    except Exception:
        return SimpleNamespace(value=value)


def _mk_tif(value: str):
    try:
        from alpaca.trading.enums import TimeInForce as AlpacaTIF  # type: ignore
        return AlpacaTIF(value)
    except Exception:
        return SimpleNamespace(value=value)


def _mk_timeframe(value: str):
    """Best-effort conversion from a string like '1Min', '1Day', '1Hour' to Alpaca TimeFrame.
    Supports multiple alpaca-py versions by trying several import paths / factories.
    """
    v = value.strip()
    try:
        # Newer alpaca-py
        from alpaca.data.timeframe import TimeFrame
        # Common aliases
        if v.lower() in {"1min", "1m"}:
            return TimeFrame.Minute
        if v.lower() in {"5min", "5m"}:
            return TimeFrame(5, TimeFrame.Unit.Minute)  # type: ignore[attr-defined]
        if v.lower() in {"15min", "15m"}:
            return TimeFrame(15, TimeFrame.Unit.Minute)  # type: ignore[attr-defined]
        if v.lower() in {"1hour", "1h"}:
            return TimeFrame.Hour
        if v.lower() in {"1day", "1d", "day"}:
            return TimeFrame.Day
        # Fallback: try to parse like '1Min'
        if v.endswith("Min"):
            n = int(v[:-3])
            return TimeFrame(n, TimeFrame.Unit.Minute)  # type: ignore[attr-defined]
        if v.endswith("Hour"):
            n = int(v[:-4])
            return TimeFrame(n, TimeFrame.Unit.Hour)  # type: ignore[attr-defined]
        return TimeFrame.Day
    except Exception:
        # Older alpaca-py variants
        try:
            from alpaca.data.timeframe import TimeFrame, TimeFrameUnit  # type: ignore
            if v.lower() in {"1min", "1m"}:
                return TimeFrame(amount=1, unit=TimeFrameUnit.Minute)
            if v.lower() in {"5min", "5m"}:
                return TimeFrame(amount=5, unit=TimeFrameUnit.Minute)
            if v.lower() in {"15min", "15m"}:
                return TimeFrame(amount=15, unit=TimeFrameUnit.Minute)
            if v.lower() in {"1hour", "1h"}:
                return TimeFrame(amount=1, unit=TimeFrameUnit.Hour)
            return TimeFrame(amount=1, unit=TimeFrameUnit.Day)
        except Exception:
            return SimpleNamespace(amount=1, unit="Day")  # very old fallback


class AlpacaAdapter(BrokerAdapter):
    def __init__(self, api_key_id: str, api_secret_key: str, env: str = "paper") -> None:
        paper = env == "paper"
        self._api_key_id = api_key_id
        self._api_secret_key = api_secret_key
        self._client = TradingClient(api_key_id, api_secret_key, paper=paper)

    @staticmethod
    def create(**kwargs: object) -> "AlpacaAdapter":
        # Credentials must be provided via kwargs (resolved from CPZ AI)
        api_key_id = str(kwargs.get("api_key_id", ""))
        api_secret_key = str(kwargs.get("api_secret_key", ""))
        env = str(kwargs.get("env", "paper"))
        
        if not api_key_id or not api_secret_key:
            raise ValueError("Alpaca credentials must be provided via CPZ AI. Do not set ALPACA_* environment variables.")
        
        return AlpacaAdapter(api_key_id=api_key_id, api_secret_key=api_secret_key, env=env)

    # --------------------- Execution ---------------------
    def get_account(self) -> Account:
        acct = self._client.get_account()
        acct_id = str(getattr(acct, "id", ""))
        buying_power = float(getattr(acct, "buying_power", 0) or 0)
        equity = float(getattr(acct, "equity", 0) or 0)
        cash = float(getattr(acct, "cash", 0) or 0)
        return Account(id=acct_id, buying_power=buying_power, equity=equity, cash=cash)

    def get_positions(self) -> list[Position]:
        raw = self._client.get_all_positions()
        positions: list[Position] = []
        for p in raw:
            symbol = str(getattr(p, "symbol", ""))
            qty = float(getattr(p, "qty", 0) or 0)
            avg_entry_price = float(getattr(p, "avg_entry_price", 0) or 0)
            market_value = float(getattr(p, "market_value", 0) or 0)
            positions.append(
                Position(symbol=symbol, qty=qty, avg_entry_price=avg_entry_price, market_value=market_value)
            )
        return positions

    def submit_order(self, req: OrderSubmitRequest) -> Order:
        side_val = req.side.value  # already lowercase
        tif_val = req.time_in_force.value.lower()
        if req.type == OrderType.MARKET:
            order = self._client.submit_order(
                order_data=MarketOrderRequest(
                    symbol=req.symbol,
                    qty=req.qty,
                    side=_mk_side(side_val),
                    time_in_force=_mk_tif(tif_val),
                )
            )
        else:
            order = self._client.submit_order(
                order_data=LimitOrderRequest(
                    symbol=req.symbol,
                    qty=req.qty,
                    side=_mk_side(side_val),
                    time_in_force=_mk_tif(tif_val),
                    limit_price=req.limit_price,
                )
            )
        return self._map_order(order)

    def get_order(self, order_id: str) -> Order:
        order = self._client.get_order_by_id(order_id)
        return self._map_order(order)

    def cancel_order(self, order_id: str) -> Order:
        self._client.cancel_order_by_id(order_id)
        return self.get_order(order_id)

    def replace_order(self, order_id: str, req: OrderReplaceRequest) -> Order:
        a_req = ReplaceOrderRequest(qty=req.qty, limit_price=req.limit_price)
        order = self._client.replace_order_by_id(order_id=order_id, order_data=a_req)
        return self._map_order(order)

    def stream_quotes(self, symbols: Iterable[str]) -> AsyncIterator[Quote]:
        async def _gen() -> AsyncIterator[Quote]:
            for sym in symbols:
                # Placeholder streaming (WS would go here)
                yield Quote(symbol=sym, bid=0.0, ask=0.0)
                break
        return _gen()

    # ----------------------- Data ------------------------
    def get_quotes(self, symbols: list[str]) -> list[Quote]:
        """Return latest quotes for the given symbols using Alpaca's market data API.
        Tries multiple alpaca-py variants for maximum compatibility.
        """
        # Try the "latest quote" endpoint first
        try:
            from alpaca.data.historical import StockHistoricalDataClient
            try:
                from alpaca.data.requests import StockLatestQuoteRequest  # newer
                client = StockHistoricalDataClient(self._api_key_id, self._api_secret_key)
                req = StockLatestQuoteRequest(symbol_or_symbols=symbols)
                resp = client.get_latest_quote(req)
                out: List[Quote] = []
                # resp can be a dict-like mapping
                for sym in symbols:
                    q = resp.get(sym) if hasattr(resp, "get") else None  # type: ignore[attr-defined]
                    if q is None:
                        continue
                    bid = float(getattr(q, "bid_price", 0) or 0)
                    ask = float(getattr(q, "ask_price", 0) or 0)
                    bid_size = float(getattr(q, "bid_size", 0) or 0)
                    ask_size = float(getattr(q, "ask_size", 0) or 0)
                    ts = getattr(q, "timestamp", None)
                    ts_dt = ts if isinstance(ts, datetime) else datetime.utcnow()
                    out.append(Quote(symbol=sym, bid=bid, ask=ask, bid_size=bid_size, ask_size=ask_size, ts=ts_dt))
                if out:
                    return out
            except ImportError:
                pass
        except Exception:
            pass

        # Fallback: get one most recent quote via get_quotes(limit=1)
        try:
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockQuotesRequest
            client = StockHistoricalDataClient(self._api_key_id, self._api_secret_key)
            req = StockQuotesRequest(symbol_or_symbols=symbols, limit=1)
            resp = client.get_quotes(req)
            out: List[Quote] = []
            # resp is typically a dict: { "AAPL": [Quote, ...], ... }
            for sym in symbols:
                items = None
                if hasattr(resp, "get"):
                    items = resp.get(sym)  # type: ignore[attr-defined]
                if items:
                    q = items[0]
                    bid = float(getattr(q, "bid_price", 0) or 0)
                    ask = float(getattr(q, "ask_price", 0) or 0)
                    bid_size = float(getattr(q, "bid_size", 0) or 0)
                    ask_size = float(getattr(q, "ask_size", 0) or 0)
                    ts = getattr(q, "timestamp", None)
                    ts_dt = ts if isinstance(ts, datetime) else datetime.utcnow()
                    out.append(Quote(symbol=sym, bid=bid, ask=ask, bid_size=bid_size, ask_size=ask_size, ts=ts_dt))
            return out
        except Exception:
            # Final fallback: return zeroed quotes to keep API stable
            return [Quote(symbol=s, bid=0.0, ask=0.0) for s in symbols]

    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> list[Bar]:
        try:
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest
        except Exception as e:
            # If market data module isn't available, return empty list as a safe fallback
            return []

        client = StockHistoricalDataClient(self._api_key_id, self._api_secret_key)
        tf = _mk_timeframe(timeframe)

        # Build request object; various alpaca-py versions accept different kwargs.
        kwargs = dict(symbol_or_symbols=symbol, timeframe=tf, limit=limit)
        if start is not None:
            kwargs["start"] = start
        if end is not None:
            kwargs["end"] = end
        try:
            req = StockBarsRequest(**kwargs)  # type: ignore[arg-type]
        except TypeError:
            # Older signature compatibility
            req = StockBarsRequest(symbol_or_symbols=symbol, timeframe=tf, limit=limit)  # type: ignore[call-arg]

        try:
            resp = client.get_bars(req)
        except Exception:
            return []

        out: list[Bar] = []
        # resp is commonly a dict-like mapping: {"AAPL": [Bar, ...]}
        seq = None
        if hasattr(resp, "get"):
            seq = resp.get(symbol)  # type: ignore[attr-defined]

        if not seq and hasattr(resp, "__iter__"):
            seq = list(resp)  # type: ignore[assignment]

        if not seq:
            return []

        for b in seq:
            o = float(getattr(b, "open", 0) or 0)
            h = float(getattr(b, "high", 0) or 0)
            l = float(getattr(b, "low", 0) or 0)
            c = float(getattr(b, "close", 0) or 0)
            v = float(getattr(b, "volume", 0) or 0)
            ts = getattr(b, "timestamp", None)
            ts_dt = ts if isinstance(ts, datetime) else datetime.utcnow()
            out.append(Bar(symbol=symbol, open=o, high=h, low=l, close=c, volume=v, ts=ts_dt))
        return out

    # --------------------- Utilities ---------------------
    @staticmethod
    def _map_order(order_obj: object) -> Order:
        oid = str(getattr(order_obj, "id", ""))
        symbol = str(getattr(order_obj, "symbol", ""))
        side_val = getattr(getattr(order_obj, "side", None), "value", getattr(order_obj, "side", "buy"))
        type_val = getattr(getattr(order_obj, "type", None), "value", getattr(order_obj, "type", "market"))
        tif_val = getattr(
            getattr(order_obj, "time_in_force", None), "value", getattr(order_obj, "time_in_force", "DAY")
        )
        status_val = getattr(getattr(order_obj, "status", None), "value", getattr(order_obj, "status", ""))
        qty_val = getattr(order_obj, "qty", 0)

        return Order(
            id=oid,
            symbol=symbol,
            side=OrderSide(str(side_val).lower()),
            qty=float(qty_val or 0),
            type=OrderType(str(type_val).lower()),
            time_in_force=TimeInForce(str(tif_val).upper()),
            status=map_order_status(str(status_val)),
        )
