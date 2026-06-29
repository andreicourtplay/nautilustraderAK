from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ib_common import PROJECT_ROOT


LOG_DIR = PROJECT_ROOT / "logs"
ORDERS_LOG = LOG_DIR / "orders.csv"
EXECUTIONS_LOG = LOG_DIR / "executions.csv"
CONNECTION_LOG = LOG_DIR / "connection_checks.log"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def append_csv(path: Path, fieldnames: list[str], row: dict[str, Any]) -> None:
    ensure_log_dir()
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in fieldnames})


def log_order_request(**row: Any) -> None:
    append_csv(
        ORDERS_LOG,
        [
            "timestamp_utc",
            "mode",
            "account",
            "client_id",
            "order_id",
            "symbol",
            "side",
            "quantity",
            "order_type",
            "limit_price",
            "tif",
            "status",
            "message",
        ],
        {"timestamp_utc": utc_now(), **row},
    )


def log_execution_summary(**row: Any) -> None:
    append_csv(
        EXECUTIONS_LOG,
        [
            "timestamp_utc",
            "account",
            "client_id",
            "symbol",
            "open_orders",
            "executions_today",
            "message",
        ],
        {"timestamp_utc": utc_now(), **row},
    )


def log_connection(message: str) -> None:
    ensure_log_dir()
    with CONNECTION_LOG.open("a", encoding="utf-8") as f:
        f.write(f"{utc_now()} {message}\n")
