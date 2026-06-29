from __future__ import annotations

import argparse
from decimal import Decimal

from ibapi.contract import Contract
from ibapi.order import Order


def build_stock_contract(args: argparse.Namespace) -> Contract:
    contract = Contract()
    contract.symbol = args.symbol.upper()
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
    order.orderRef = f"nautilus-paper-{args.symbol.lower()}"
    order.whatIf = not args.submit_paper_order
    order.transmit = True

    if args.order_type == "LMT":
        if args.limit_price is None:
            raise ValueError("--limit-price is required for LMT orders")
        order.lmtPrice = float(args.limit_price)

    order.contract = build_stock_contract(args)
    return order
