from __future__ import annotations

import argparse
import asyncio
import os
from decimal import Decimal

from ibapi.contract import Contract
from ibapi.order import Order

from ib_common import account_id_from_env
from ib_common import create_nautilus_ib_client
from ib_common import ensure_managed_accounts
from ib_common import env_int
from ib_common import load_project_env
from ib_common import resolve_ib_endpoint
from ib_common import tcp_reachable
from ib_logging import log_execution_summary
from ib_logging import log_order_request
from ib_safety import validate_order_request


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Submit an Interactive Brokers paper order through NautilusTrader.",
    )
    p.add_argument("--symbol", default=os.getenv("IB_ORDER_SYMBOL", "AAPL"))
    p.add_argument("--side", choices=("BUY", "SELL"), default=os.getenv("IB_ORDER_ACTION", "BUY"))
    p.add_argument("--quantity", default=os.getenv("IB_ORDER_QUANTITY", "1"))
    p.add_argument("--order-type", choices=("MKT", "LMT"), default=os.getenv("IB_ORDER_TYPE", "MKT"))
    p.add_argument("--limit-price", type=float, default=None)
    p.add_argument("--currency", default=os.getenv("IB_ORDER_CURRENCY", "USD"))
    p.add_argument("--exchange", default=os.getenv("IB_ORDER_EXCHANGE", "SMART"))
    p.add_argument("--primary-exchange", default=os.getenv("IB_ORDER_PRIMARY_EXCHANGE", "NASDAQ"))
    p.add_argument("--tif", default=os.getenv("IB_ORDER_TIF", "DAY"))
    p.add_argument("--wait-seconds", type=int, default=10)
    p.add_argument(
        "--submit-paper-order",
        action="store_true",
        help="Actually transmit the order to the IB paper account. Without this, sends whatIf only.",
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


def build_stock_contract(args: argparse.Namespace) -> Contract:
    contract = Contract()
    contract.symbol = args.symbol
    contract.secType = "STK"
    contract.exchange = args.exchange
    contract.currency = args.currency
    if args.primary_exchange:
        contract.primaryExchange = args.primary_exchange
    return contract


def build_order(args: argparse.Namespace, account_id: str, order_id: int) -> Order:
    order = Order()
    order.orderId = order_id
    order.action = args.side
    order.orderType = args.order_type
    order.totalQuantity = Decimal(str(args.quantity))
    order.account = account_id
    order.clearingAccount = account_id
    order.tif = args.tif
    order.orderRef = f"nautilus-paper-demo-{args.symbol.lower()}"
    order.whatIf = not args.submit_paper_order
    order.transmit = True

    if args.order_type == "LMT":
        if args.limit_price is None:
            raise ValueError("--limit-price is required for LMT orders")
        order.lmtPrice = float(args.limit_price)

    order.contract = build_stock_contract(args)
    return order


async def run_order(args: argparse.Namespace) -> int:
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

    print(f"using IB endpoint {endpoint.host}:{endpoint.port} with client_id={client_id}")
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

        order_id = client.next_order_id()
        order = build_order(args, account_id, order_id)
        mode = "paper submit" if args.submit_paper_order else "whatIf"
        message = (
            f"sending {mode}: {order.action} {order.totalQuantity} {order.contract.symbol} "
            f"{order.orderType} account={account_id} order_id={order_id}"
        )
        print(message)
        log_order_request(
            mode=mode,
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

        open_orders = await client.get_open_orders(account_id)
        executions = await client.get_executions(account_id)
        open_count = "unknown" if open_orders is None else str(len(open_orders))
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
    return asyncio.run(run_order(args))


if __name__ == "__main__":
    raise SystemExit(main())
