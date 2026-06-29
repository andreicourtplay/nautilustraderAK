from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


DEFAULT_ALLOWED_SYMBOLS = ("AAPL", "IBKR")


@dataclass(frozen=True)
class PaperSafetyConfig:
    require_paper_account: bool
    max_order_quantity: Decimal
    allowed_symbols: tuple[str, ...]


def decimal_from_text(value: str, field_name: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be a valid number") from exc
    if result <= 0:
        raise ValueError(f"{field_name} must be greater than zero")
    return result


def load_safety_config() -> PaperSafetyConfig:
    allowed = os.getenv("IB_ALLOWED_SYMBOLS", ",".join(DEFAULT_ALLOWED_SYMBOLS))
    allowed_symbols = tuple(symbol.strip().upper() for symbol in allowed.split(",") if symbol.strip())
    max_quantity = decimal_from_text(os.getenv("IB_MAX_ORDER_QUANTITY", "1"), "IB_MAX_ORDER_QUANTITY")
    require_paper = os.getenv("IB_REQUIRE_PAPER_ACCOUNT", "true").strip().lower() not in {
        "0",
        "false",
        "no",
    }
    return PaperSafetyConfig(
        require_paper_account=require_paper,
        max_order_quantity=max_quantity,
        allowed_symbols=allowed_symbols or DEFAULT_ALLOWED_SYMBOLS,
    )


def validate_paper_account(account_id: str, allow_non_paper_account: bool = False) -> None:
    config = load_safety_config()
    if allow_non_paper_account or not config.require_paper_account:
        return
    if not account_id.upper().startswith("DU"):
        raise ValueError(
            f"Refusing non-paper-looking account {account_id!r}. "
            "Paper accounts normally start with DU.",
        )


def validate_order_request(
    *,
    account_id: str,
    symbol: str,
    quantity: str | Decimal,
    submit: bool,
    confirmed: bool,
    allow_non_paper_account: bool = False,
) -> None:
    config = load_safety_config()
    validate_paper_account(account_id, allow_non_paper_account)

    normalized_symbol = symbol.upper()
    if normalized_symbol not in config.allowed_symbols:
        raise ValueError(
            f"Symbol {normalized_symbol!r} is not in IB_ALLOWED_SYMBOLS={','.join(config.allowed_symbols)}",
        )

    requested_quantity = quantity if isinstance(quantity, Decimal) else decimal_from_text(quantity, "quantity")
    if requested_quantity > config.max_order_quantity:
        raise ValueError(
            f"Quantity {requested_quantity} exceeds IB_MAX_ORDER_QUANTITY={config.max_order_quantity}",
        )

    if submit and not confirmed:
        raise ValueError("Refusing to submit. Add --confirm-paper-trade to send a paper order.")
