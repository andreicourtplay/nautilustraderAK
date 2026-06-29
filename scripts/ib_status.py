from __future__ import annotations

import argparse
import asyncio
import os
from typing import Any

from ib_common import account_id_from_env
from ib_common import create_nautilus_ib_client
from ib_common import ensure_managed_accounts
from ib_common import env_int
from ib_common import load_project_env
from ib_common import resolve_ib_endpoint
from ib_common import tcp_reachable
from ib_logging import log_connection
from ib_safety import validate_paper_account


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Show IBKR paper account status through NautilusTrader.")
    p.add_argument("--account", default=None, help="Override IB_ACCOUNT/TWS_ACCOUNT from .env.")
    p.add_argument("--positions", action="store_true", help="Show positions only.")
    p.add_argument("--open-orders", action="store_true", help="Show open orders only.")
    p.add_argument("--executions", action="store_true", help="Show executions only.")
    p.add_argument(
        "--allow-non-paper-account",
        action="store_true",
        help="Override the DU-account guard for status reads.",
    )
    return p


def value(obj: Any, *names: str, default: str = "") -> str:
    for name in names:
        if hasattr(obj, name):
            raw = getattr(obj, name)
            if raw is not None:
                return str(raw)
    return default


def iter_collection(collection: Any) -> list[Any]:
    if collection is None:
        return []
    if isinstance(collection, dict):
        return list(collection.values())
    return list(collection)


def describe_position(position: Any) -> str:
    instrument = value(position, "instrument_id", "instrument", "symbol", default="?")
    qty = value(position, "quantity", "qty", "signed_qty", default="?")
    avg_px = value(position, "avg_px_open", "avg_px", "average_cost", default="?")
    return f"{instrument} qty={qty} avg_px={avg_px}"


def describe_order(order: Any) -> str:
    instrument = value(order, "instrument_id", "instrument", "symbol", default="?")
    side = value(order, "side", "action", default="?")
    qty = value(order, "quantity", "totalQuantity", "qty", default="?")
    order_type = value(order, "order_type", "orderType", default="?")
    status = value(order, "status", "order_state", default="?")
    return f"{instrument} {side} qty={qty} type={order_type} status={status}"


def describe_execution(execution: Any) -> str:
    instrument = value(execution, "instrument_id", "symbol", "contract", default="?")
    side = value(execution, "side", "action", default="?")
    qty = value(execution, "quantity", "shares", "qty", default="?")
    price = value(execution, "price", "avg_price", "avgPrice", default="?")
    return f"{instrument} {side} qty={qty} price={price}"


def should_show(args: argparse.Namespace, flag: str) -> bool:
    explicit = args.positions or args.open_orders or args.executions
    return getattr(args, flag) or not explicit


async def run_status(args: argparse.Namespace) -> int:
    load_project_env()
    os.environ.setdefault("IB_MAX_CONNECTION_ATTEMPTS", "1")

    account_id = args.account or account_id_from_env()
    if not account_id:
        print("Set IB_ACCOUNT or TWS_ACCOUNT in .env first.")
        return 2

    try:
        validate_paper_account(account_id, args.allow_non_paper_account)
    except ValueError as exc:
        print(str(exc))
        return 2

    endpoint = resolve_ib_endpoint()
    client_id = env_int("IB_CLIENT_ID", 101)
    connection_timeout = env_int("IB_CONNECTION_TIMEOUT", 30)
    request_timeout = env_int("IB_REQUEST_TIMEOUT", 20)

    print(f"checking IB status at {endpoint.host}:{endpoint.port} with client_id={client_id}")
    if not tcp_reachable(endpoint.host, endpoint.port):
        print("IB API is not reachable. Start TWS/IB Gateway paper and retry.")
        log_connection(f"status not reachable endpoint={endpoint.host}:{endpoint.port}")
        return 2

    client = create_nautilus_ib_client(endpoint, client_id, request_timeout)

    try:
        client.start()
        await client.wait_until_ready(connection_timeout)

        accounts = sorted(await ensure_managed_accounts(client))
        if account_id not in accounts:
            print(f"Configured account {account_id!r} not returned by IB: {accounts}")
            return 2

        print(f"account: {account_id}")

        if should_show(args, "positions"):
            positions = await client.get_positions(account_id)
            position_items = iter_collection(positions)
            print(f"positions: {len(position_items)}")
            for position in position_items:
                print(f"  - {describe_position(position)}")

        if should_show(args, "open_orders"):
            open_orders = await client.get_open_orders(account_id)
            order_items = iter_collection(open_orders)
            print(f"open_orders: {len(order_items)}")
            for order in order_items:
                print(f"  - {describe_order(order)}")

        if should_show(args, "executions"):
            executions = await client.get_executions(account_id)
            execution_items = iter_collection(executions)
            print(f"executions_today: {len(execution_items)}")
            for execution in execution_items:
                print(f"  - {describe_execution(execution)}")

        log_connection(f"status ok account={account_id}")
        return 0
    finally:
        if client.is_running:
            client.stop()
            await asyncio.sleep(1)


def main() -> int:
    args = parser().parse_args()
    return asyncio.run(run_status(args))


if __name__ == "__main__":
    raise SystemExit(main())
