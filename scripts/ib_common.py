from __future__ import annotations

import os
import socket
import asyncio
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IB_PORT_CANDIDATES = (7497, 4002, 7496, 4001)
LOCALHOSTS = {"127.0.0.1", "localhost"}


@dataclass(frozen=True)
class IBEndpoint:
    host: str
    port: int


def load_project_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value in (None, "") else int(value)


def tcp_reachable(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def resolve_ib_endpoint() -> IBEndpoint:
    host = os.getenv("IB_GATEWAY_HOST", "127.0.0.1")
    port_value = os.getenv("IB_GATEWAY_PORT")

    if port_value:
        return IBEndpoint(host=host, port=int(port_value))

    if host not in LOCALHOSTS:
        return IBEndpoint(host=host, port=7497)

    for port in DEFAULT_IB_PORT_CANDIDATES:
        if tcp_reachable(host, port):
            return IBEndpoint(host=host, port=port)

    return IBEndpoint(host=host, port=7497)


def account_id_from_env() -> str | None:
    return os.getenv("IB_ACCOUNT") or os.getenv("TWS_ACCOUNT")


async def ensure_managed_accounts(client, timeout: float = 8.0) -> set[str]:
    accounts = client.accounts()
    if accounts:
        return accounts

    # TWS normally emits managedAccounts on connect, but reconnections can race.
    req = getattr(getattr(client, "_eclient", None), "reqManagedAccts", None)
    if callable(req):
        req()

    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        accounts = client.accounts()
        if accounts:
            return accounts
        await asyncio.sleep(0.2)

    return client.accounts()


def create_nautilus_ib_client(endpoint: IBEndpoint, client_id: int, request_timeout: int):
    from nautilus_trader.adapters.interactive_brokers.client import InteractiveBrokersClient
    from nautilus_trader.cache.cache import Cache
    from nautilus_trader.common.component import LiveClock
    from nautilus_trader.common.component import MessageBus
    from nautilus_trader.model.identifiers import TraderId

    clock = LiveClock()
    msgbus = MessageBus(TraderId(os.getenv("NAUTILUS_TRADER_ID", "TRADER-001")), clock)
    cache = Cache()

    return InteractiveBrokersClient(
        loop=asyncio.get_running_loop(),
        msgbus=msgbus,
        cache=cache,
        clock=clock,
        host=endpoint.host,
        port=endpoint.port,
        client_id=client_id,
        request_timeout_secs=request_timeout,
    )
