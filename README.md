# NautilusTrader + Interactive Brokers paper setup

This folder is a local NautilusTrader project prepared for Interactive Brokers paper/demo.

## Installed

- Python virtual environment: `.venv`
- NautilusTrader: `nautilus-trader[ib]`
- Helper scripts under `scripts/`
- IB paper configuration template: `config/ib_paper.env.example`

## Verify install

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/check_install.py
```

## Configure IB paper

1. Open TWS or IB Gateway logged into the paper/demo account.
2. Enable API socket access in TWS/IB Gateway.
3. Use one of the common paper ports:
   - TWS paper: `7497`
   - IB Gateway paper: `4002`
4. If you want to submit orders, disable read-only API for the paper session.
5. Copy the env template and edit the account:

```bash
cp config/ib_paper.env.example .env
```

Set `IB_ACCOUNT` / `TWS_ACCOUNT` to your paper account ID, normally starting with `DU`.

## Working With Two People

Use Git branches for code, and a separate local `.env` per computer. Do not share or commit credentials.

See [docs/COLLABORATION.md](docs/COLLABORATION.md).

Recommended long-lived development branches:

- `dev/andrei`
- `dev/fran`

## Check connection

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/ib_connection_check.py
```

The check connects through NautilusTrader's Interactive Brokers client and prints returned accounts, positions count, and open order count.

## Paper order workflow

Default is `whatIf`, which asks IB to simulate margin/commission and does not place the order:

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/ib_paper_order.py --symbol AAPL --side BUY --quantity 1
```

To actually transmit a paper/demo order:

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/ib_paper_order.py --symbol AAPL --side BUY --quantity 1 --submit-paper-order --confirm-paper-trade
```

The submit path refuses non-`DU` accounts unless you pass `--allow-non-paper-account`.

Additional paper safety defaults are configured in `.env`:

- `IB_REQUIRE_PAPER_ACCOUNT=true`
- `IB_MAX_ORDER_QUANTITY=1`
- `IB_ALLOWED_SYMBOLS=AAPL,IBKR`

## Status and logs

Review the current paper account state:

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/ib_status.py
```

Local runtime logs are written under `logs/`:

- `logs/connection_checks.log`
- `logs/orders.csv`
- `logs/executions.csv`

The real log files are ignored by Git.
