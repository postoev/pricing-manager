# CLAUDE.md — Project Guide for Claude Code

## Commands

```bash
pipx run market_sim.py [args]   # run simulation (CLI)
pipx run run_tests.py           # run all 34 tests
jupyter notebook market_sim.ipynb  # interactive notebook
```

## Architecture

```
market/
├── goods.py        # Good — demand model (MNL logit)
├── assortment.py   # Assortment — container for all market goods
├── seller.py       # Seller — budget, price history, padding helpers
├── strategies.py   # Strategy protocol + EpsilonGreedy + GradientAscent
├── simulation.py   # Market — core simulation loop
├── factory.py      # build_market — random market generation
└── visualization.py  # plot_simulation (matplotlib, not imported in tests)

market_sim.py       # thin CLI layer — no business logic here
market_sim.ipynb    # interactive notebook (ipywidgets, step-by-step simulation)
run_tests.py        # pipx-runnable test runner
tests/              # pytest tests, one file per module
```

## Key Design Decisions

**Demand model** — MNL (multinomial logit). A buyer's purchase is a single draw:
- weights: `[1.0 (outside option)] + [exp(λ(V−pᵢ)) for each seller]`
- outcome `-1` = no purchase; outcome `k` = buy from seller k
- Adding sellers at same price grows total market (outside option shrinks) — this is intentional and correct

**Assortment** — `Assortment` is the single source of truth for all goods on the market. Supports mapping-like access (`__getitem__`, `__contains__`, `__iter__`), `add(good)`, `names()`, `items()`, `values()`, `cost_range()`, `optimal_prices()`, `summary()`. `Market` holds an `Assortment`; pass it from `build_market` or construct manually.

**Seller budget** — `budget: float` is a required positional argument (third, after `name` and `goods`). It is updated in `record()` as `budget += profit` after each day's sales. Factory initialises all sellers with `10_000.0`.

**Strategies** — `Strategy` is a `Protocol` with `__call__(seller, good, cost) -> float`.
Add a new strategy: dataclass with `__call__`, add to `REGISTRY` in `strategies.py`. No other changes needed.

`cost` must be used as the lower bound for any price proposal — prices below cost yield negative margin on every unit sold regardless of demand, so that region must never be explored. Use `max(cost, ...)` in exploration, not an external clamp.

**Padding** — sellers have shorter histories if created with a non-default `start_day`. `Seller.profit_series(n_days)` and `sales_series(good, n_days)` zero-pad from the left based on `start_day`. Use these methods when aggregating across sellers — never pad manually in other modules.

**visualization.py** — sets `matplotlib.use('Agg')` at import time. Not imported in `market/__init__.py` deliberately, so tests never touch matplotlib. `_smooth` uses `mode='valid'` convolution and returns an aligned x-axis to avoid zero-padding artifacts at series edges.

## Constraints

- Sellers only observe their own sales — they do not see competitors' prices or sales
- Prices are fixed per day and updated simultaneously after each day
- Cost is fixed and identical for the same good across all sellers
- `Good.value` and `Good.lam` are hidden from sellers (they learn implicitly via sales)
- Prices are hard-floored at `cost × 1.001` in `Market._update_prices`

## Python Version

Requires Python ≥ 3.10 (uses `dict[str, ...]` and `set[str]` as type annotations).
Runtime: Python 3.12.3 (WSL).
