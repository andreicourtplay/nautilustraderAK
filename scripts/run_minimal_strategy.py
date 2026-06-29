from __future__ import annotations

import argparse
import asyncio
import os
import sys

from ib_common import PROJECT_ROOT
from ib_common import account_id_from_env
from ib_common import create_nautilus_ib_client
from ib_common import ensure_managed_accounts
from ib_common import env_int
from ib_common import load_project_env
from ib_common import resolve_ib_endpoint
from ib_common import tcp_reachable
from ib_logging import log_execution_summary
from ib_logging import log_order_request
from ib_logging import log_strategy_decision
from ib_orders import build_order
from ib_safety import validate_order_request
from ib_status import iter_collection


sys.path.insert(0, str(PROJECT_ROOT))

from strategies.single_symbol_entry import StrategyDecision  # noqa: E402
from strategies.single_symbol_entry import decide_single_symbol_entry  # noqa: E402


STRATEGY_NAME = "single_symbol_entry"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run the first controlled IBKR paper strategy.",
    )
    p.add_argument("--symbol", default=os.getenv("IB_STRATEGY_SYMBOL", os.getenv("IB_ORDER_SYMBOL", "AAPL")))
    p.add_argument("--side", choices=("BUY", "SELL"), default=os.getenv("IB_STRATEGY_SIDE", "BUY"))
    p.add_argument("--quantity", default=os.getenv("IB_STRATEGY_QUANTITY", os.getenv("IB_ORDER_QUANTITY", "1")))
    p.add_argument("--order-type", choices=("MKT", "LMT"), default=os.getenv("IB_STRATEGY_ORDER_TYPE", "MKT"))
    p.add_argument("--limit-price", type=float, default=None)
    p.add_argument("--currency", default=os.getenv("IB_ORDER_CURRENCY", "USD"))
    p.add_argument("--exchange", default=os.getenv("IB_ORDER_EXCHANGE", "SMART"))
    p.add_argument("--primary-exchange", default=os.getenv("IB_ORDER_PRIMARY_EXCHANGE", "NASDAQ"))
    p.add_argument("--tif", default=os.getenv("IB_ORDER_TIF", "DAY"))
    p.add_argument("--wait-seconds", type=int, default=10)
    p.add_argument(
        "--allow-add-to-position",
        action="store_true",
        help="Allow the strategy to create an order even if a position already exists.",
    )
    p.add_argument(
        "--allow-with-open-orders",
        action="store_true",
        help="Allow the strategy to create an order while open orders exist.",
    )
    p.add_argument(
        "--submit-paper-order",
        action="store_true",
        help="Actually transmit a paper order. Without this, sends whatIf only.",
    )
    p.add_argument(
        "--confirm-paper-trade",
        action="store_true",
        help="Required together with --submit-paper-order.",
    )
    p.add_argument(
        "--allow-non-paper-account",
        action="store_true",
        help="Override the DU-account guard. Use only if you know this is still a demo endpoint.",
    )
    return p


def print_decision(decision: StrategyDecision, mode: str) -> None:
    print(
        f"decision={decision.action} mode={mode} symbol={decision.symbol} side={decision.side} "
        f"quantity={decision.quantity} position={decision.current_position} "
        f"open_orders={decision.open_orders} reason={decision.reason}",
    )


def log_decision(
    *,
    decision: StrategyDecision,
    mode: str,
    account_id: str,
    client_id: int,
) -> None:
    log_strategy_decision(
        strategy=STRATEGY_NAME,
        mode=mode,
        account=account_id,
        client_id=client_id,
        symbol=decision.symbol,
        side=decision.side,
        quantity=str(decision.quantity),
        decision=decision.action,
        reason=decision.reason,
        current_position=str(decision.current_position),
        open_orders=decision.open_orders,
    )


async def run_strategy(args: argparse.Namespace) -> int:
    load_project_env()
    os.environ.setdefault("IB_MAX_CONNECTION_ATTEMPTS", "1")

    account_id = account_id_from_env()
    if not account_id:
        print("Set IB_ACCOUNT or TWS_ACCOUNT in .env first.")
        return 2

    try:
        validate_order_request(
            account_id=account_id,
            symbol=args.symbol,
            quantity=args.quantity,
            submit=args.submit_paper_order,
            confirmed=args.confirm_paper_trade,
            allow_non_paper_account=args.allow_non_paper_account,
        )
    except ValueError as exc:
        print(str(exc))
        return 2

    endpoint = resolve_ib_endpoint()
    client_id = env_int("IB_CLIENT_ID", 101)
    connection_timeout = env_int("IB_CONNECTION_TIMEOUT", 30)
    request_timeout = env_int("IB_REQUEST_TIMEOUT", 20)
    mode = "paper submit" if args.submit_paper_order else "whatIf"

    print(f"running {STRATEGY_NAME} at {endpoint.host}:{endpoint.port} with client_id={client_id}")
    if not tcp_reachable(endpoint.host, endpoint.port):
        print("IB API is not reachable. Start TWS/IB Gateway paper and retry.")
        return 2

    client = create_nautilus_ib_client(endpoint, client_id, request_timeout)

    try:
        client.start()
        await client.wait_until_ready(connection_timeout)

        accounts = await ensure_managed_accounts(client)
        if account_id not in accounts:
            print(f"Configured account {account_id!r} not returned by IB: {sorted(accounts)}")
            return 2

        positions = iter_collection(await client.get_positions(account_id))
        open_orders = iter_collection(await client.get_open_orders(account_id))
        decision = decide_single_symbol_entry(
            symbol=args.symbol,
            side=args.side,
            quantity=args.quantity,
            positions=positions,
            open_orders=open_orders,
            allow_add_to_position=args.allow_add_to_position,
            allow_with_open_orders=args.allow_with_open_orders,
        )
        print_decision(decision, mode)
        log_decision(decision=decision, mode=mode, account_id=account_id, client_id=client_id)

        if not decision.should_order:
            return 0

        order_id = client.next_order_id()
        order = build_order(args, account_id, order_id)
        message = (
            f"strategy sending {mode}: {order.action} {order.totalQuantity} "
            f"{order.contract.symbol} {order.orderType} account={account_id} order_id={order_id}"
        )
        print(message)
        log_order_request(
            mode=f"strategy {mode}",
            account=account_id,
            client_id=client_id,
            order_id=order_id,
            symbol=order.contract.symbol,
            side=order.action,
            quantity=str(order.totalQuantity),
            order_type=order.orderType,
            limit_price=getattr(order, "lmtPrice", ""),
            tif=order.tif,
            status="sent",
            message=message,
        )
        client.place_order(order)

        await asyncio.sleep(args.wait_seconds)

        open_orders_after = await client.get_open_orders(account_id)
        executions = await client.get_executions(account_id)
        open_count = "unknown" if open_orders_after is None else str(len(open_orders_after))
        execution_count = "unknown" if executions is None else str(len(executions))
        summary = f"post-check: open_orders={open_count}, executions_today={execution_count}"
        print(summary)
        log_execution_summary(
            account=account_id,
            client_id=client_id,
            symbol=args.symbol.upper(),
            open_orders=open_count,
            executions_today=execution_count,
            message=summary,
        )
        return 0
    finally:
        if client.is_running:
            client.stop()
            await asyncio.sleep(1)


def main() -> int:
    load_project_env()
    args = parser().parse_args()
    return asyncio.run(run_strategy(args))


if __name__ == "__main__":
    raise SystemExit(main())
