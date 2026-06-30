from __future__ import annotations

import csv
import json
from dataclasses import asdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

from strategies.single_symbol_entry import decide_single_symbol_entry


@dataclass(frozen=True)
class PriceBar:
    date: str
    symbol: str
    close: Decimal


@dataclass(frozen=True)
class BacktestTrade:
    date: str
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    reason: str


@dataclass(frozen=True)
class BacktestSummary:
    symbol: str
    side: str
    quantity: Decimal
    start_date: str
    end_date: str
    entry_price: Decimal | None
    exit_price: Decimal | None
    completed_trades: int
    gross_pnl: Decimal
    win_rate_pct: Decimal
    max_drawdown: Decimal
    final_position: Decimal
    ending_equity: Decimal


def read_price_bars(path: Path, symbol: str) -> list[PriceBar]:
    bars: list[PriceBar] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["symbol"].upper() != symbol.upper():
                continue
            bars.append(
                PriceBar(
                    date=row["date"],
                    symbol=row["symbol"].upper(),
                    close=Decimal(row["close"]),
                ),
            )
    if not bars:
        raise ValueError(f"No price bars found for {symbol!r} in {path}")
    return bars


def mock_position(symbol: str, quantity: Decimal):
    return SimpleNamespace(contract=SimpleNamespace(symbol=symbol), quantity=quantity)


def max_drawdown(equity_curve: list[Decimal]) -> Decimal:
    if not equity_curve:
        return Decimal("0")
    peak = equity_curve[0]
    worst = Decimal("0")
    for equity in equity_curve:
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > worst:
            worst = drawdown
    return worst


def run_minimal_backtest(
    *,
    bars: list[PriceBar],
    symbol: str,
    side: str,
    quantity: Decimal,
    starting_cash: Decimal,
    force_flat_at_end: bool = True,
) -> tuple[BacktestSummary, list[BacktestTrade], list[dict[str, str]]]:
    normalized_symbol = symbol.upper()
    normalized_side = side.upper()
    cash = starting_cash
    position = Decimal("0")
    entry_price: Decimal | None = None
    exit_price: Decimal | None = None
    trades: list[BacktestTrade] = []
    decisions: list[dict[str, str]] = []
    equity_curve: list[Decimal] = []

    for bar in bars:
        positions = [mock_position(normalized_symbol, position)] if position else []
        decision = decide_single_symbol_entry(
            symbol=normalized_symbol,
            side=normalized_side,
            quantity=quantity,
            positions=positions,
            open_orders=[],
        )
        decisions.append(
            {
                "date": bar.date,
                "symbol": normalized_symbol,
                "decision": decision.action,
                "reason": decision.reason,
                "position_before": str(position),
                "close": str(bar.close),
            },
        )

        if decision.should_order and position == 0:
            signed_qty = quantity if normalized_side == "BUY" else -quantity
            cash -= signed_qty * bar.close
            position += signed_qty
            entry_price = bar.close
            trades.append(
                BacktestTrade(
                    date=bar.date,
                    symbol=normalized_symbol,
                    side=normalized_side,
                    quantity=quantity,
                    price=bar.close,
                    reason=decision.reason,
                ),
            )

        equity_curve.append(cash + position * bar.close)

    if force_flat_at_end and position != 0:
        last = bars[-1]
        exit_side = "SELL" if position > 0 else "BUY"
        exit_qty = abs(position)
        cash += position * last.close
        exit_price = last.close
        trades.append(
            BacktestTrade(
                date=last.date,
                symbol=normalized_symbol,
                side=exit_side,
                quantity=exit_qty,
                price=last.close,
                reason="forced flat at end of sample",
            ),
        )
        position = Decimal("0")
        equity_curve.append(cash)

    gross_pnl = cash - starting_cash
    completed_trades = 1 if entry_price is not None and exit_price is not None else 0
    win_rate = Decimal("100") if completed_trades and gross_pnl > 0 else Decimal("0")
    summary = BacktestSummary(
        symbol=normalized_symbol,
        side=normalized_side,
        quantity=quantity,
        start_date=bars[0].date,
        end_date=bars[-1].date,
        entry_price=entry_price,
        exit_price=exit_price,
        completed_trades=completed_trades,
        gross_pnl=gross_pnl,
        win_rate_pct=win_rate,
        max_drawdown=max_drawdown(equity_curve),
        final_position=position,
        ending_equity=cash,
    )
    return summary, trades, decisions


def decimal_default(value):
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def write_summary(path: Path, summary: BacktestSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(asdict(summary), f, indent=2, default=decimal_default)
        f.write("\n")


def write_trades(path: Path, trades: list[BacktestTrade]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["date", "symbol", "side", "quantity", "price", "reason"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for trade in trades:
            writer.writerow(
                {
                    "date": trade.date,
                    "symbol": trade.symbol,
                    "side": trade.side,
                    "quantity": str(trade.quantity),
                    "price": str(trade.price),
                    "reason": trade.reason,
                },
            )


def write_decisions(path: Path, decisions: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["date", "symbol", "decision", "reason", "position_before", "close"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(decisions)
