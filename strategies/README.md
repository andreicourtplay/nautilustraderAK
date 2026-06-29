# Strategies

This folder is reserved for NautilusTrader strategy code.

Current rule: strategy work starts only after the paper-only guards, logs, and
manual status/order scripts are working reliably.

Planned first strategy:

1. Read `.env` and safety limits.
2. Connect to the IBKR paper account.
3. Check the current position for a single allowed symbol.
4. If no position exists, create a small paper-only order or whatIf simulation.
5. Log the decision, order request, and post-check result.
