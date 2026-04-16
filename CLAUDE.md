# CLAUDE.md — Project Guide for Claude Code

## Commands

```bash
pipx run market_sim.py [args]   # run simulation
pipx run run_tests.py           # run all 36 tests
```

## Architecture

```
market/
├── goods.py        # Good — demand model (MNL logit)
├── seller.py       # Seller — price history, padding helpers
├── events.py       # Event — market structure changes
├── strategies.py   # Strategy protocol + EpsilonGreedy + GradientAscent
├── simulation.py   # Market — core simulation loop
├── factory.py      # build_market — random market generation
└── visualization.py  # plot_simulation (matplotlib, not imported in tests)

market_sim.py       # thin CLI layer — no business logic here
run_tests.py        # pipx-runnable test runner
tests/              # pytest tests, one file per module
```

## Key Design Decisions

**Demand model** — MNL (multinomial logit). A buyer's purchase is a single draw:
- weights: `[1.0 (outside option)] + [exp(λ(V−pᵢ)) for each seller]`
- outcome `-1` = no purchase; outcome `k` = buy from seller k
- Adding sellers at same price grows total market (outside option shrinks) — this is intentional and correct

**Strategies** — `Strategy` is a `Protocol` with `__call__(seller, good, cost) -> float`.
Add a new strategy: dataclass with `__call__`, add to `REGISTRY` in `strategies.py`. No other changes needed.

**Events** — dispatched via `dict[kind, handler]` in `Market._apply_event`. To add a new event type: add a handler method `_handle_<kind>` and register it in the dict.

**Padding** — sellers that enter mid-simulation have shorter histories. `Seller.profit_series(n_days)` and `sales_series(good, n_days)` zero-pad from the left based on `start_day`. Use these methods when aggregating across sellers of different ages — never pad manually in other modules.

**visualization.py** — sets `matplotlib.use('Agg')` at import time. Not imported in `market/__init__.py` deliberately, so tests never touch matplotlib.

## Constraints

- Sellers only observe their own sales — they do not see competitors' prices or sales
- Prices are fixed per day and updated simultaneously after each day
- Cost is fixed and identical for the same good across all sellers
- `Good.value` and `Good.lam` are hidden from sellers (they learn implicitly via sales)
- Prices are hard-floored at `cost × 1.001` in `Market._update_prices`

## Python Version

Requires Python ≥ 3.10 (uses `dict[str, ...]` and `set[str]` as type annotations).
Runtime: Python 3.12.3 (WSL).
