# Minimal backtest workflow

This project has an offline minimal backtest for the first controlled strategy.

It does not connect to TWS, IBKR, market data, or any live account. It uses a
small sample CSV to validate the flow:

1. read prices;
2. run the same entry decision used by the paper strategy;
3. enter once if the strategy returns `ORDER`;
4. skip while a position exists;
5. force-close at the final bar for reporting;
6. write summary, trades, and decisions.

## Run the sample backtest

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_sample_backtest.py
```

Default input:

```text
data/samples/ibkr_daily_sample.csv
```

Default output:

```text
data/backtests/latest/
```

Generated files:

- `summary.json`
- `trades.csv`
- `decisions.csv`

The generated result files are local and ignored by Git. The sample input CSV is
safe and committed.

## Current sample result

With the included IBKR sample data:

```text
completed_trades: 1
gross_pnl: 6.05
win_rate_pct: 100
max_drawdown: 0.45
final_position: 0
ending_equity: 100006.05
```

This is not a trading edge. It is a test harness proving that decisions, trades,
metrics, and output files work.

## Useful variants

Use another symbol if the CSV contains it:

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_sample_backtest.py --symbol IBKR
```

Keep the final position open instead of force-closing it:

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_sample_backtest.py --keep-open-position
```

Write results to a custom folder:

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_sample_backtest.py --output-dir data/backtests/test-run-001
```

## Next improvement

The next backtest step should replace the sample CSV with real historical data
or an exported dataset, then compare strategy variants before any additional
paper order submission.
