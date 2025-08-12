# Exchange

## Energy Trading in a Nutshell

Energy trading happens in an exchange, a market where traders working for energy producers (solar plants,
nuclear power plants, ...) and consumers (B2C energy providers, big energy-consuming industries
like steel and trains...) submit orders to buy and sell energy.
One of the major exchanges in Europe is called [EPEX](https://en.wikipedia.org/wiki/European_Power_Exchange).

These orders consist of a volume (in Megawatt, rounded to one decimal) over a predefined period of time,
called delivery period (for example between 12:00, the delivery start and 13:00, the delivery end, on a given day)
and for a given price per megawatt hour (referred to as MWh).
If the prices of two orders with opposite sides match, i.e., the buy price is higher than the sell price, then, a trade
is generated.
For example, if the orderbook contains an order to sell 10 MW for 10 euros/MWh and another trader submits
an order to buy 5 MW for 11 euros/MWh, the orders are matched by the exchange and a trade is generated for 5 MW at
10 euros/MWh.

## Trades (or private trades)

A list of trades that our trading floor executed is provided by the exchange as a JSON.
Volumes are in megawatt, and prices are in euro per MWh.
A trade also has a delivery start and a delivery end, defining the time range for which the volume was traded.
This range can either span an hour or a quarter-hour, but an hourly trade could also be seen as four quarter-hourly
trades. For example,

```
side=SELL volume=10.0 MW price=10.0 Euro delivery_start=2025-06-01 01:00:00 delivery_end=2025-06-01 02:00:00
```

is equivalent to

```
side=SELL volume=10.0 MW price=10.0 Euro delivery_start=2025-06-01 01:00:00 delivery_end=2025-06-01 01:15:00
side=SELL volume=10.0 MW price=10.0 Euro delivery_start=2025-06-01 01:15:00 delivery_end=2025-06-01 01:30:00
side=SELL volume=10.0 MW price=10.0 Euro delivery_start=2025-06-01 01:30:00 delivery_end=2025-06-01 01:45:00
side=SELL volume=10.0 MW price=10.0 Euro delivery_start=2025-06-01 01:45:00 delivery_end=2025-06-01 02:00:00
```

In real life, trades come in continuously, as they happen, through, for example, a websocket connection. To simplify
for this challenge, we will only look at an end-of-day file downloaded from the trading system.

## Revenue and PnL

The trading revenues are calculated by multiplying the volume with the price over all trades: for a buy trade,
the revenue is negative, for a sell trade, the revenue is positive.
The pnl is defined as the difference between the income made selling energy and the cost made buying it for a given
quarter-hour.
If we sell energy, our income is `quantity * price` since we got money for our electricity.
If we buy energy, our income is `-quantity * price`.
The PnL timeseries has a quarter-hourly resolution and for each quarter-hour, we add up the revenue for all trades for
which the delivery range contains the quarter-hourly timestamp.
For example, to compute the PnL for the timestamp `2025-06-01T10:15:00Z`, we consider (quarter-hourly) trades having
the delivery range `2025-06-01T10:15:00Z` to `2025-06-01T10:30:00Z` and (hourly) trades having the delivery range
`2025-06-01T10:00:00Z` to `2025-06-01T11:00:00Z`.

## Public Trades

The exchange also provides a list of trades that were executed by all exchange participants, also called **public trades**.
As for private trades, public trades would also be coming in continuously through a websocket connection but for this
challenge we are only looking at an end-of-day export, provided by the exchange as a csv file.

## VWAPs

Given a list of trades (public or private), we can define a **volume weighted average price** (also called VWAP)
quarter-hourly timeseries, as the sum of the revenue divided by the buy plus sell volume.
For example, to compute the VWAP for the timestamp `2025-06-01T10:15:00Z`, we consider (quarter-hourly) trades having
the delivery range `2025-06-01T10:15:00Z` to `2025-06-01T10:30:00Z` and (hourly) trades having the delivery range
`2025-06-01T10:00:00Z` to `2025-06-01T11:00:00Z`.

We can calculate this quantity based on the private trades and it can be understood as a measure of the performance of
our trading if we compare it to the VWAP computed based on the public trades.
This is one example of a market **index** that can be built, but there are many more that give the traders insights on
price movements and feedback on their trading decisions.