from __future__ import annotations

import asyncio
import os

from ib_common import account_id_from_env
from ib_common import create_nautilus_ib_client
from ib_common import ensure_managed_accounts
from ib_common import env_int
from ib_common import load_project_env
from ib_common import resolve_ib_endpoint
from ib_common import tcp_reachable
from ib_logging import log_connection


async def run_check() -> int:
    load_project_env()
    os.environ.setdefault("IB_MAX_CONNECTION_ATTEMPTS", "1")

    endpoint = resolve_ib_endpoint()
    client_id = env_int("IB_CLIENT_ID", 101)
    connection_timeout = env_int("IB_CONNECTION_TIMEOUT", 30)
    request_timeout = env_int("IB_REQUEST_TIMEOUT", 20)
    expected_account = account_id_from_env()

    print(f"checking IB endpoint {endpoint.host}:{endpoint.port} with client_id={client_id}")
    log_connection(f"checking endpoint={endpoint.host}:{endpoint.port} client_id={client_id}")

    if not tcp_reachable(endpoint.host, endpoint.port):
        print("IB API is not reachable.")
        print("Open TWS/IB Gateway paper and enable API sockets, then retry.")
        print("Common paper ports: TWS=7497, IB Gateway=4002.")
        log_connection(f"not reachable endpoint={endpoint.host}:{endpoint.port}")
        return 2

    client = create_nautilus_ib_client(endpoint, client_id, request_timeout)

    try:
        client.start()
        await client.wait_until_ready(connection_timeout)

        accounts = sorted(await ensure_managed_accounts(client))
        print("connected via NautilusTrader Interactive Brokers client")
        print("accounts: " + (", ".join(accounts) if accounts else "(none returned)"))
        log_connection(f"connected accounts={','.join(accounts) if accounts else '(none)'}")

        if expected_account and expected_account not in accounts:
            print(f"warning: configured account {expected_account!r} was not returned by IB")

        for account_id in accounts:
            positions = await client.get_positions(account_id)
            open_orders = await client.get_open_orders(account_id)
            pos_count = "unknown" if positions is None else str(len(positions))
            order_count = "unknown" if open_orders is None else str(len(open_orders))
            print(f"{account_id}: positions={pos_count}, open_orders={order_count}")
            log_connection(f"account={account_id} positions={pos_count} open_orders={order_count}")

        return 0
    finally:
        if client.is_running:
            client.stop()
            await asyncio.sleep(1)


def main() -> int:
    return asyncio.run(run_check())


if __name__ == "__main__":
    raise SystemExit(main())
