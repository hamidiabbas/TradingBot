#!/usr/bin/env python3
"""
Batch-run every strategy in strategies/ with
EnhancedRealDataBacktestingEngine and write

• results/<Strategy>.json – full engine output
• results/scoreboard.csv  – one-line summary per strategy

Example
-------
python batch_backtest.py --symbol EURUSD --timeframe H1 \
                         --start 2023-01-01 --end 2024-12-31
"""
import argparse
import importlib.util
import inspect
import json
import sys
import time
import traceback
from pathlib import Path

import pandas as pd
from tqdm import tqdm

# ---------------------------------------------------------------------
# 0.  Make the Windows console accept emoji / UTF-8 log messages
# ---------------------------------------------------------------------
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------
# 1.  CLI
# ---------------------------------------------------------------------
p = argparse.ArgumentParser()
p.add_argument("--symbol",    default="EURUSD")
p.add_argument("--timeframe", default="H1")
p.add_argument("--start",     default=None, help="YYYY-MM-DD")
p.add_argument("--end",       default=None, help="YYYY-MM-DD")
p.add_argument("--datas",     nargs="*", default=[],
               help="optional custom CSV/H5 paths")
p.add_argument("--engine",    default="enhanced_backtesting_engine.py",
               help="filename of the big engine (leave default if unchanged)")
p.add_argument("--risk",      type=float, default=0.02, help="risk per trade")
args = p.parse_args()

# ---------------------------------------------------------------------
# 1a.  Parse dates and make them tz-aware (UTC)
# ---------------------------------------------------------------------
start_date = pd.to_datetime(args.start) if args.start else None
end_date   = pd.to_datetime(args.end)   if args.end   else None
if start_date is not None and start_date.tzinfo is None:
    start_date = start_date.tz_localize("UTC")
if end_date is not None and end_date.tzinfo is None:
    end_date = end_date.tz_localize("UTC")

# ---------------------------------------------------------------------
# 2.  Import the back-testing engine dynamically
# ---------------------------------------------------------------------
engine_path = Path(args.engine).resolve()
spec        = importlib.util.spec_from_file_location("enh_engine", engine_path)
eng_module  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eng_module)                 # type: ignore[attr-defined]
Engine = eng_module.EnhancedRealDataBacktestingEngine  # noqa: N806

# ---------------------------------------------------------------------
# 3.  Discover strategies
# ---------------------------------------------------------------------
strat_dir = Path("strategies")
sys.path.append(str(strat_dir.resolve()))
strategies = {}
for py in strat_dir.glob("*.py"):
    if py.stem.startswith("_"):
        continue
    m   = importlib.util.spec_from_file_location(py.stem, py)
    mod = importlib.util.module_from_spec(m)
    try:
        m.loader.exec_module(mod)                   # type: ignore[attr-defined]
    except Exception:
        print(f"⚠️  {py.name} import failed:")
        traceback.print_exc()
        continue
    for _, cls in inspect.getmembers(mod, inspect.isclass):
        if hasattr(cls, "generate_signals") or hasattr(cls, "analyze"):
            try:
                strategies[cls.__name__] = cls()
            except Exception:
                continue

if not strategies:
    print("No strategies discovered — aborting.")
    sys.exit(1)

# ---------------------------------------------------------------------
# 4.  Run back-tests
# ---------------------------------------------------------------------
results_root = Path("results")
results_root.mkdir(exist_ok=True)

score_rows = []
for s_name, strat in tqdm(strategies.items(), desc="Strategies"):
    e = Engine(risk_per_trade=args.risk)
    try:
        t0  = time.perf_counter()
        res = e.run_comprehensive_backtest(
            symbol=args.symbol,
            timeframe=args.timeframe,
            strategy=strat,
            data_sources=args.datas if args.datas else None,
            start_date=start_date,
            end_date=end_date,
        )
        elapsed = time.perf_counter() - t0

        # 4a. save full JSON
        out_json = results_root / f"{s_name}.json"
        with open(out_json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, default=str, indent=2)

        # 4b. scoreboard line  (PortfolioMetrics attributes)
        perf = res["performance_metrics"]
        score_rows.append({
            "strategy":        s_name,
            "net_profit":      perf.net_profit,
            "total_return_%":  perf.total_return * 100,
            "sharpe":          perf.sharpe_ratio,
            "max_dd_%":        perf.max_drawdown * 100,
            "trades":          perf.total_trades,
            "win_rate_%":      perf.win_rate * 100,
            "runtime_s":       round(elapsed, 2),
        })
        print(f"✅ {s_name:25}  PnL ${perf.net_profit:,.0f}   "
              f"Sharpe {perf.sharpe_ratio:.2f}   "
              f"DD {perf.max_drawdown:.1%}   {elapsed:.1f}s")
    except Exception:
        print(f"❌ {s_name} blew up — see traceback below")
        traceback.print_exc()

# ---------------------------------------------------------------------
# 5.  Save scoreboard
# ---------------------------------------------------------------------
if score_rows:
    df = pd.DataFrame(score_rows).sort_values("net_profit", ascending=False)
    df.to_csv(results_root / "scoreboard.csv", index=False)
    print("\n=== SCOREBOARD ===")
    print(df.to_string(
        index=False,
        formatters={
            "net_profit":      "{:,.0f}".format,
            "total_return_%":  "{:.1f}".format,
            "max_dd_%":        "{:.1f}".format,
            "win_rate_%":      "{:.1f}".format}))
    print(f"\nFull JSON results per strategy are in {results_root.resolve()}")
else:
    print("No strategy finished successfully.")
