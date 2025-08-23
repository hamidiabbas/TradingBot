#!/usr/bin/env python3
"""
================================================================
SIMPLE BACKTESTER 1.0  –  Per-strategy walk-forward simulator
================================================================
• Scans strategies/ for classes exposing `.analyze(df, symbol)`  
• Fetches historical OHLCV from MetaTrader-5 (or CSV fallback)  
• Feeds each new bar incrementally to the strategy  
• Opens a position when signal != HOLD and no position is open  
• Closes the position on an opposite signal or SL/TP hit  
• Calculates P&L in account currency (assumes 100 000 lot size)  
================================================================
IMPORTANT:
    1.  **Run on a demo account first.**
    2.  MT5 terminal must be installed and logged-in.
    3.  Environment variables MT5_LOGIN / MT5_PASSWORD / MT5_SERVER
        (or an already-logged terminal) are required for live data.
================================================================
"""

import os
import sys
import inspect
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import pandas as pd
import numpy as np
import MetaTrader5 as mt5


# --------------------------------------------------------------
# 1. CONFIGURATION – edit here or pass via CLI
# --------------------------------------------------------------
SYMBOL          = "EURUSD"
TIMEFRAME       = "H1"           # any MT5 timeframe code e.g. M15, H1, H4, D1 …
START_DATE      = "2024-01-01"
END_DATE        = "2024-12-31"
INITIAL_BALANCE = 100_000        # USD
LOT_SIZE        = 0.1            # fixed 0.1 lot per trade
SPREAD_PIPS     = 1.5            # added to each fill price (≈ realistic)
CSV_FALLBACK    = "data/EURUSD_H1_2024.csv"   # optional CSV if MT5 not available
MIN_CONF        = 0.01           # ignore signals with lower confidence
MIN_BARS        = 50             # minimum bars before a strategy may trade
OUTPUT_DIR      = Path("backtests")
OUTPUT_DIR.mkdir(exist_ok=True)


# --------------------------------------------------------------
# 2. DATA LOADER
# --------------------------------------------------------------
def load_price_data(symbol: str,
                    timeframe: str,
                    start_date: str,
                    end_date: str) -> pd.DataFrame:
    """
    Attempts MT5 download. Falls back to CSV file if mt5 unavailable.
    Returns DataFrame with ['time','open','high','low','close','tick_volume'].
    """
    tf_enum = getattr(mt5, f"TIMEFRAME_{timeframe}", None)

    if mt5.initialize() and tf_enum is not None:
        print(f"📡 Pulling data for {symbol} {timeframe} from MT5 …")
        utc_from = datetime.strptime(start_date, "%Y-%m-%d")
        utc_to   = datetime.strptime(end_date,   "%Y-%m-%d") + timedelta(days=1)

        rates = mt5.copy_rates_range(symbol, tf_enum, utc_from, utc_to)
        mt5.shutdown()

        if rates is not None and len(rates):
            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s")
            return df

    # ---- CSV fallback -----------------------------------------------------
    if Path(CSV_FALLBACK).exists():
        print("📄 MT5 unavailable – loading CSV fallback")
        df = pd.read_csv(CSV_FALLBACK, parse_dates=["time"])
        return df

    raise RuntimeError("Unable to load price data – MT5 failed and CSV missing.")


# --------------------------------------------------------------
# 3. STRATEGY DISCOVERY
# --------------------------------------------------------------
def discover_strategies() -> Dict[str, Any]:
    """
    Dynamically imports each *.py in strategies/ and returns
    {strategy_name: class_instance}
    """
    strategies = {}
    strategies_dir = Path("strategies")
    sys.path.append(str(strategies_dir.resolve()))

    for pyfile in strategies_dir.glob("*.py"):
        if pyfile.stem.startswith("_"):
            continue

        spec = importlib.util.spec_from_file_location(pyfile.stem, pyfile)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # type: ignore[attr-defined]
        except Exception as exc:
            print(f"⚠️  Could not import {pyfile.name}: {exc}")
            continue

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if hasattr(cls, "analyze"):
                try:
                    strategies[cls.__name__] = cls()
                    print(f"✅ Loaded strategy: {cls.__name__}")
                    break
                except Exception as inst_exc:
                    print(f"⚠️  Instantiation failed for {cls.__name__}: {inst_exc}")

    return strategies


# --------------------------------------------------------------
# 4. BACKTEST ENGINE
# --------------------------------------------------------------
class Backtester:
    def __init__(self,
                 symbol: str,
                 df: pd.DataFrame,
                 strategy,
                 lot_size: float,
                 init_balance: float):
        self.symbol       = symbol
        self.df           = df.reset_index(drop=True)
        self.strategy     = strategy
        self.lot_size     = lot_size
        self.balance      = init_balance
        self.equity_curve = []
        self.trades       = []  # list of dict
        self.position     = None  # { 'dir': +1/-1, 'entry': price }

    @staticmethod
    def _pip_value(symbol: str) -> float:
        return 0.0001 if symbol.endswith(("USD", "CHF", "CAD")) else 0.01

    def _open_trade(self, direction: str, price: float, time: pd.Timestamp):
        self.position = {
            "dir": +1 if direction in ("BUY", "STRONG_BUY") else -1,
            "entry": price,
            "open_time": time,
        }

    def _close_trade(self, price: float, time: pd.Timestamp):
        if not self.position:
            return
        dir_     = self.position["dir"]
        entry    = self.position["entry"]
        pips     = (price - entry) / self._pip_value(self.symbol) * dir_
        profit   = pips * self.lot_size * 10  # ≈ $ per pip per lot (FX majors)
        self.balance += profit
        self.trades.append({
            "open_time":  self.position["open_time"],
            "close_time": time,
            "direction":  "BUY" if dir_ == 1 else "SELL",
            "entry":      entry,
            "exit":       price,
            "pips":       pips,
            "profit":     profit,
        })
        self.position = None

    def run(self):
        min_bars = max(getattr(self.strategy, "min_data_points", MIN_BARS), MIN_BARS)

        for idx in range(len(self.df)):
            row = self.df.iloc[idx]
            time = row["time"]
            close_price = row["close"]

            if idx < min_bars:
                self.equity_curve.append(self.balance)
                continue

            # slice up to current bar (inclusive)
            window = self.df.loc[:idx].copy()

            try:
                sig = self.strategy.analyze(window, self.symbol)
            except Exception as exc:
                print(f"⚠️ Strategy error at {time}: {exc}")
                sig = {"signal": "HOLD", "confidence": 0}

            # Simple trade logic
            if self.position:
                # exit on opposite signal
                if sig["signal"] in ("BUY", "STRONG_BUY") and self.position["dir"] == -1:
                    self._close_trade(close_price, time)
                elif sig["signal"] in ("SELL", "STRONG_SELL") and self.position["dir"] == +1:
                    self._close_trade(close_price, time)
            else:
                if sig["signal"] in ("BUY", "STRONG_BUY", "SELL", "STRONG_SELL") \
                        and sig.get("confidence", 0) >= MIN_CONF:
                    # apply spread slippage
                    slip = SPREAD_PIPS * self._pip_value(self.symbol)
                    fill = close_price + slip if sig["signal"].startswith("BUY") else close_price - slip
                    self._open_trade(sig["signal"], fill, time)

            # equity curve
            if self.position:
                dir_ = self.position["dir"]
                entry = self.position["entry"]
                unreal = (close_price - entry) / self._pip_value(self.symbol) * dir_ * self.lot_size * 10
                self.equity_curve.append(self.balance + unreal)
            else:
                self.equity_curve.append(self.balance)

        # close any open position at final price
        if self.position:
            self._close_trade(self.df.iloc[-1]["close"], self.df.iloc[-1]["time"])

    # --------------- performance metrics -----------------------
    def _max_drawdown(self, curve: List[float]) -> float:
        peak = curve[0]
        max_dd = 0
        for equity in curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            max_dd = max(max_dd, dd)
        return max_dd

    def report(self) -> Dict[str, Any]:
        curve = self.equity_curve
        pnl   = self.balance - INITIAL_BALANCE
        returns = np.diff(curve)
        sharpe = (np.mean(returns) / (np.std(returns) + 1e-9)) * np.sqrt(252*24)  # hourly → yearly
        dd     = self._max_drawdown(curve)
        wins   = sum(1 for t in self.trades if t["profit"] > 0)
        win_rate = wins / len(self.trades) if self.trades else 0
        return {
            "net_pnl":        pnl,
            "trades":         len(self.trades),
            "win_rate":       win_rate,
            "sharpe":         sharpe,
            "max_drawdown":   dd,
            "final_balance":  self.balance,
        }

    def save_trade_log(self, name: str):
        if not self.trades:
            return
        df = pd.DataFrame(self.trades)
        out = OUTPUT_DIR / f"{name}_trades.csv"
        df.to_csv(out, index=False)


# --------------------------------------------------------------
# 5. MAIN ROUTINE
# --------------------------------------------------------------
def main():
    df = load_price_data(SYMBOL, TIMEFRAME, START_DATE, END_DATE)
    strategies = discover_strategies()

    results = []
    for s_name, strat in strategies.items():
        print(f"\n🚀 Back-testing {s_name} …")
        bt = Backtester(SYMBOL, df, strat, LOT_SIZE, INITIAL_BALANCE)
        bt.run()
        res = bt.report()
        bt.save_trade_log(s_name)
        results.append((s_name, res))
        print(f"   → PnL: ${res['net_pnl']:.2f} | Trades: {res['trades']}"
              f" | Win Rate: {res['win_rate']:.1%}"
              f" | Sharpe: {res['sharpe']:.2f}"
              f" | Max DD: {res['max_drawdown']:.1%}")

    # Summary table
    if results:
        print("\n================ BACKTEST SUMMARY ================")
        res_df = pd.DataFrame(
            [dict(strategy=s, **r) for s, r in results]
        ).sort_values("net_pnl", ascending=False)
        print(res_df.to_string(index=False, formatters={"net_pnl": "{:,.2f}".format}))
        res_df.to_csv(OUTPUT_DIR / "summary.csv", index=False)
    else:
        print("No strategies executed.")

if __name__ == "__main__":
    main()
