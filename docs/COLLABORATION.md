# Two-person workflow

The repo can be shared, but runtime data must stay local.

## Git branches

Use one branch per person or per task:

```bash
git checkout dev/andrei
git checkout dev/fran
```

Keep `main` as the stable branch. Merge through pull requests or reviewed merges.

Branch policy:

- `main`: stable base that should run install and connection checks.
- `dev/andrei`: Andrei's working branch.
- `dev/fran`: Fran's working branch.
- short task branches can be created from each personal branch when needed.

## Local configuration

Each person creates their own `.env` on their own computer:

```bash
cp .env.example .env
```

The `.env` file is ignored by Git and must never be committed. It contains each person's:

- IB paper account ID
- local TWS/Gateway port
- `IB_CLIENT_ID`
- `NAUTILUS_TRADER_ID`

Suggested split:

```bash
# Person 1
IB_CLIENT_ID=101
NAUTILUS_TRADER_ID=TRADER-ANDREI

# Person 2
IB_CLIENT_ID=102
NAUTILUS_TRADER_ID=TRADER-FRAN
```

If each person runs their own local TWS/Gateway on their own computer, duplicate `IB_CLIENT_ID` values are not a socket conflict. Still, unique IDs make logs and order origin clearer.

If both connect to the same TWS/Gateway instance, `IB_CLIENT_ID` must be different.

## Interactive Brokers sessions

Best setup:

- each person uses their own IB username;
- each person runs TWS or IB Gateway locally;
- each person uses paper/demo first;
- each person keeps their own `.env`;
- code changes go through branches.

If both operate the same IB account, agree risk limits before enabling live order submission. The project scripts default to `whatIf` and require explicit flags before transmitting paper orders.

## Setup on the second computer

```bash
git clone <repo-url>
cd <repo-folder>
uv sync
cp .env.example .env
```

Then edit `.env`, open TWS/IB Gateway paper, and run:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/check_install.py
UV_CACHE_DIR=.uv-cache uv run python scripts/ib_connection_check.py
```

## Do not commit

Do not commit:

- `.env`
- credentials
- local logs
- `.venv`
- `.uv-cache`
- local market data exports

## Remote branch setup

Once the GitHub remote is configured, push the stable branch and the two working branches:

```bash
git push -u origin main
git push -u origin dev/andrei
git push -u origin dev/fran
```
