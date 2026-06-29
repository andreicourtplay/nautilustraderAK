# First controlled strategy workflow

This project now has a minimal strategy runner for IBKR paper testing.

## What it does

The first strategy is intentionally simple:

1. Connect to TWS/IB Gateway paper.
2. Read the configured paper account.
3. Read current positions and open orders.
4. For one symbol, decide whether to skip or prepare an order.
5. Log the decision under `logs/strategy_decisions.csv`.
6. If it decides to order, send `whatIf` by default.

It is not designed to make money. It validates the operating flow.

## Default command

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_minimal_strategy.py
```

With the default `.env`, this checks `AAPL`. If you already have an AAPL
position, the expected result is `decision=SKIP`.

## Test the order path safely

Use an allowed symbol with no current position. The default still uses `whatIf`,
so it does not transmit a real paper order:

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_minimal_strategy.py --symbol IBKR
```

## Paper submission

Only transmit a paper order after checking the decision and logs:

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_minimal_strategy.py --symbol IBKR --submit-paper-order --confirm-paper-trade
```

The safety layer still blocks non-paper accounts, quantities above
`IB_MAX_ORDER_QUANTITY`, and symbols outside `IB_ALLOWED_SYMBOLS`.

## Review after each run

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/ib_status.py
```

Then review local logs:

- `logs/strategy_decisions.csv`
- `logs/orders.csv`
- `logs/executions.csv`
