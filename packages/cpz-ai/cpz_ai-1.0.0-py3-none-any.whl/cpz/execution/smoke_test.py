from datetime import datetime, timedelta

from cpz.execution.router import BrokerRouter
from cpz.execution.enums import OrderSide, OrderType, TimeInForce
from cpz.execution.models import OrderSubmitRequest


router = BrokerRouter.default()  # will auto-register cpz-native and use it if no alpaca creds

# 1) Quotes
qs = router.get_quotes(["AAPL", "MSFT"])
print("Quotes:", [(q.symbol, q.bid, q.ask) for q in qs])

# 2) Historical bars
bars = router.get_historical_data("AAPL", timeframe="1Min", limit=5)
print("Bars:", [(b.ts.isoformat(), b.open, b.high, b.low, b.close, b.volume) for b in bars])

# 3) Account/positions
acct = router.get_account()
print("Account:", acct)

# 4) Market buy then sell
buy = OrderSubmitRequest(symbol="AAPL", side=OrderSide.BUY, qty=10, type=OrderType.MARKET, time_in_force=TimeInForce.DAY)
o1 = router.submit_order(buy)
print("Buy order status:", o1.status)
sell = OrderSubmitRequest(symbol="AAPL", side=OrderSide.SELL, qty=10, type=OrderType.MARKET, time_in_force=TimeInForce.DAY)
o2 = router.submit_order(sell)
print("Sell order status:", o2.status)

# 5) Limit order workflow
lim = OrderSubmitRequest(symbol="MSFT", side=OrderSide.BUY, qty=5, type=OrderType.LIMIT, time_in_force=TimeInForce.DAY, limit_price=95.0)
o3 = router.submit_order(lim)
print("Limit order initial:", o3.status)
o3b = router.replace_order(o3.id, type("R", (), {"qty": None, "limit_price": 999.0})())  # naive replace
print("Limit order after replace:", o3b.status)

# 6) Positions check
positions = router.get_positions()
print("Positions:", positions)
