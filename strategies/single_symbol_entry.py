from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class StrategyDecision:
    action: str
    reason: str
    symbol: str
    side: str
    quantity: Decimal
    current_position: Decimal
    open_orders: int

    @property
    def should_order(self) -> bool:
        return self.action == "ORDER"


def object_value(obj: Any, *names: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        for name in names:
            if name in obj and obj[name] is not None:
                return obj[name]
        return default
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return default


def contract_symbol(obj: Any) -> str:
    contract = object_value(obj, "contract")
    symbol = object_value(contract, "symbol", "localSymbol", default="")
    if symbol:
        return str(symbol).upper()
    return str(object_value(obj, "symbol", "instrument_id", default="")).upper()


def position_quantity_for_symbol(positions: list[Any], symbol: str) -> Decimal:
    normalized_symbol = symbol.upper()
    total = Decimal("0")
    for position in positions:
        if contract_symbol(position) != normalized_symbol:
            continue
        quantity = object_value(position, "quantity", "qty", "signed_qty", default="0")
        total += Decimal(str(quantity))
    return total


def decide_single_symbol_entry(
    *,
    symbol: str,
    side: str,
    quantity: str | Decimal,
    positions: list[Any],
    open_orders: list[Any],
    allow_add_to_position: bool = False,
    allow_with_open_orders: bool = False,
) -> StrategyDecision:
    normalized_symbol = symbol.upper()
    normalized_side = side.upper()
    requested_quantity = quantity if isinstance(quantity, Decimal) else Decimal(str(quantity))
    current_position = position_quantity_for_symbol(positions, normalized_symbol)
    open_order_count = len(open_orders)

    if open_order_count > 0 and not allow_with_open_orders:
        return StrategyDecision(
            action="SKIP",
            reason="open orders already exist",
            symbol=normalized_symbol,
            side=normalized_side,
            quantity=requested_quantity,
            current_position=current_position,
            open_orders=open_order_count,
        )

    if current_position != 0 and not allow_add_to_position:
        return StrategyDecision(
            action="SKIP",
            reason=f"existing position for {normalized_symbol}: {current_position}",
            symbol=normalized_symbol,
            side=normalized_side,
            quantity=requested_quantity,
            current_position=current_position,
            open_orders=open_order_count,
        )

    return StrategyDecision(
        action="ORDER",
        reason="no existing position or blocking open orders",
        symbol=normalized_symbol,
        side=normalized_side,
        quantity=requested_quantity,
        current_position=current_position,
        open_orders=open_order_count,
    )
