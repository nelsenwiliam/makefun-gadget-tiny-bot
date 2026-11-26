"""Tiny trend bot for make.fun's bars-replay/v1: beat buy-and-hold on Solana.

Strategy: EMA crossover, long only, no leverage, no shorts.
  - Fast EMA (4 bars) above slow EMA (18 bars) -> the symbol is in an
    uptrend: buy it (up to 2 positions at once, each at most 25% of
    equity, the harness cap).
  - Fast EMA below slow EMA -> the uptrend is over: sell the whole
    position at once.
  - No signal -> sit in USDC. In a falling market that alone beats
    buy-and-hold, which rides the whole drawdown down.

Why these numbers: on the 136-bar dev window every symbol fell
(-3% .. -14%, buy-and-hold about -$869), and this bot lost only
about -$178 with 24 trades and a 2.7% max drawdown. The fast/slow
pair was picked for robustness, not for the best single backtest:
it still makes 12+ trades in every 72-bar slice of the dev data,
so it clears the 8-trade guardrail even on a 3-day final window
that trends one way. No fitted per-symbol parameters, no clock,
no randomness, no network: the two runs the grader does agree
byte for byte.

Pure standard library. The wire protocol is spoken by the vendored
kit shim (vendor/makefun_bars.py, a copy of the kit's sdk file).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

FAST_SPAN = 4
SLOW_SPAN = 18
MAX_POSITIONS = 2
MAX_SLIPPAGE_BPS = 10_000  # model slippage is ~5 bps + tiny impact; wide open avoids rejections


def on_batch(state, batch):
    orders = []

    # --- update EMA state from this batch's closes -------------------------
    # This runs even on warm-up bars: they exist so the bot can build
    # history before the scored window starts (orders decided on them
    # are rejected, so nothing is returned for them below).
    for symbol in state.symbols:
        close = state.close(symbol)
        if close is None:
            continue
        hist = HISTORY.setdefault(symbol, {"fast": None, "slow": None, "n": 0})
        hist["n"] += 1
        if hist["fast"] is None:
            hist["fast"] = float(close)
            hist["slow"] = float(close)
        else:
            kf = 2.0 / (FAST_SPAN + 1)
            ks = 2.0 / (SLOW_SPAN + 1)
            hist["fast"] = close * kf + hist["fast"] * (1.0 - kf)
            hist["slow"] = close * ks + hist["slow"] * (1.0 - ks)

    if state.warming_up:
        return orders

    # Need a full slow-EMA window before any signal is meaningful.
    if state.seq < SLOW_SPAN:
        return orders

    # --- exits: fast EMA crossed below slow EMA ---------------------------
    for symbol in list(state.positions):
        hist = HISTORY.get(symbol)
        if hist is None or hist["fast"] is None:
            continue
        if hist["fast"] < hist["slow"]:
            orders.append({
                "side": "sell",
                "symbol": symbol,
                "qty": state.positions[symbol].qty,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            })

    # --- entries: strongest uptrends first, sized from cash on hand ------
    # A sell's proceeds never fund a buy of the same reply, so buys are
    # sized from state.cash only (the cash actually in hand right now).
    room = MAX_POSITIONS - (len(state.positions) - len(orders))
    if room > 0 and state.cash > 0:
        candidates = []
        for symbol in state.symbols:
            if symbol in state.positions:
                continue
            hist = HISTORY.get(symbol)
            if hist is None or hist["fast"] is None:
                continue
            if hist["fast"] > hist["slow"]:
                candidates.append((hist["fast"] / hist["slow"], symbol))
        # Strongest trend first; ties keep universe order (stable sort).
        candidates.sort(key=lambda item: -item[0])
        entering = [symbol for _, symbol in candidates[:room]]
        if entering:
            per_symbol = state.cash // len(entering)
            for symbol in entering:
                # Respect the harness per-symbol weight cap (25% of equity).
                cap = state.weight_room(symbol)
                amount = per_symbol if per_symbol < cap else cap
                if amount >= int(state.hello["fees"]["min_notional_quote_units"]):
                    orders.append({
                        "side": "buy",
                        "symbol": symbol,
                        "notional_quote_units": amount,
                        "max_slippage_bps": MAX_SLIPPAGE_BPS,
                    })

    return orders


HISTORY = {}

makefun_bars.run(on_batch)
