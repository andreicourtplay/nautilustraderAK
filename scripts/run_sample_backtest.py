from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

from ib_common import PROJECT_ROOT


sys.path.insert(0, str(PROJECT_ROOT))

from backtests.minimal_backtest import read_price_bars
from backtests.minimal_backtest import run_minimal_backtest
from backtests.minimal_backtest import write_decisions
from backtests.minimal_backtest import write_summary
from backtests.minimal_backtest import write_trades


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the offline minimal strategy backtest.")
    p.add_argument("--symbol", default="IBKR")
    p.add_argument("--side", choices=("BUY", "SELL"), default="BUY")
    p.add_argument("--quantity", default="1")
    p.add_argument("--starting-cash", default="100000")
    p.add_argument(
        "--prices",
        type=Path,
        default=PROJECT_ROOT / "data" / "samples" / "ibkr_daily_sample.csv",
        help="CSV with date,symbol,close columns.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "backtests" / "latest",
        help="Directory where summary/trades/decisions files are written.",
    )
    p.add_argument(
        "--keep-open-position",
        action="store_true",
        help="Do not force-close the position on the last bar.",
    )
    return p


def main() -> int:
    args = parser().parse_args()
    bars = read_price_bars(args.prices, args.symbol)
    summary, trades, decisions = run_minimal_backtest(
        bars=bars,
        symbol=args.symbol,
        side=args.side,
        quantity=Decimal(str(args.quantity)),
        starting_cash=Decimal(str(args.starting_cash)),
        force_flat_at_end=not args.keep_open_position,
    )

    output_dir = args.output_dir
    write_summary(output_dir / "summary.json", summary)
    write_trades(output_dir / "trades.csv", trades)
    write_decisions(output_dir / "decisions.csv", decisions)

    print(f"backtest written to: {output_dir}")
    print(f"symbol: {summary.symbol}")
    print(f"period: {summary.start_date} to {summary.end_date}")
    print(f"completed_trades: {summary.completed_trades}")
    print(f"gross_pnl: {summary.gross_pnl}")
    print(f"win_rate_pct: {summary.win_rate_pct}")
    print(f"max_drawdown: {summary.max_drawdown}")
    print(f"final_position: {summary.final_position}")
    print(f"ending_equity: {summary.ending_equity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
