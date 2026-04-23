# CLAUDE.md — Project Guide for Claude Code

## Commands

```bash
pipx run market_sim.py [args]   # run simulation (CLI)
pipx run run_tests.py           # run all 57 tests
jupyter notebook market_sim.ipynb  # interactive notebook
```

## Architecture

```
market/
├── goods.py           # Good — demand model (MNL logit)
├── assortment.py      # Assortment — container for all market goods
├── catalog.py         # GoodsCatalog — CSV persistence for assortment (data/assortment.csv)
├── seller.py          # Seller — budget, prices, delegates to metrics + stock
├── metrics.py         # GoodMetrics, SellerMetrics — time-series history per entity
├── pricing_strategies.py  # PricingStrategy protocol + EpsilonGreedy + GradientAscent
├── stock_manager.py   # StockManager — per-seller inventory (purchase/consume)
├── stock_strategies.py  # StockStrategy protocol + FixedStock + BudgetFraction + STOCK_REGISTRY
├── simulation.py      # Market — core simulation loop (purchase → price → simulate)
├── factory.py         # build_market — loads catalog or generates goods on first run
└── visualization.py   # plot_simulation (matplotlib, not imported in tests)

data/
└── assortment.csv     # persistent good catalog (created on first run, not committed)

market_sim.py       # thin CLI layer — no business logic here
market_sim.ipynb    # interactive notebook — step-by-step simulator (see below)
run_tests.py        # pipx-runnable test runner
tests/              # pytest tests, one file per module
```

## Key Design Decisions

**Demand model** — MNL (multinomial logit). A buyer's purchase is a single draw:
- weights: `[1.0 (outside option)] + [exp(λ(V−pᵢ)) for each seller]`
- outcome `-1` = no purchase; outcome `k` = buy from seller k
- Adding sellers at same price grows total market (outside option shrinks) — this is intentional and correct

**Good identity** — `Good` has a required `id: str` field (first) that is the primary key everywhere: `Assortment._goods`, `Seller.goods`, `Seller.prices`, `Seller.good_metrics`, and the CSV catalog. `Good.name` is the human-readable label used only for display. Fields in order: `id`, `name`, `cost`, `value`, `lam`, `description`.

**Assortment** — `Assortment` is the single source of truth for all goods on the market. Keyed by `good.id`. Supports mapping-like access (`__getitem__`, `__contains__`, `__iter__`), `add(good)`, `ids()`, `items()`, `values()`, `cost_range()`, `optimal_prices()`, `summary()`. `Market` holds an `Assortment`; pass it from `build_market` or construct manually.

**Catalog** — `market/catalog.py` provides CSV persistence at `data/assortment.csv`. Functions: `is_initialized(path)`, `load(path) -> list[Good]`, `save(goods, path)`, `generate(n, rng) -> list[Good]`. The built-in template has 20 realistic consumer goods (Bread, Milk, Eggs …). `factory.py` loads from the catalog if it exists, otherwise calls `generate()` and saves. The catalog is the single source of truth for good IDs across runs.

**Seller budget** — `budget: float` is a required positional argument (third, after `name` and `goods`). It is updated in `record()` as `budget += profit` after each day's sales. Factory initialises all sellers with `10_000.0`.

**Strategies** — `PricingStrategy` is a `Protocol` with `__call__(seller, good_id, cost) -> float`.
Add a new strategy: dataclass with `__call__`, add to `PRICING_REGISTRY` in `strategies.py`. No other changes needed.

`cost` must be used as the lower bound for any price proposal — prices below cost yield negative margin on every unit sold regardless of demand, so that region must never be explored. Use `max(cost, ...)` in exploration, not an external clamp.

**Metrics** — historical data lives in `market/metrics.py`, not in `Seller`. `GoodMetrics` tracks one seller's per-good time series (prices, sales, profit, stock). `SellerMetrics` tracks seller-level budget history. A shared module-level `_padded()` handles zero-padding for late-entry sellers. Access via `seller.good_metrics[good_id]` and `seller.seller_metrics`. The pattern is ready for `MarketGoodMetrics` or any other entity that needs time-series tracking.

**Stock management** — `StockManager` (in `stock_manager.py`) is an internal per-seller inventory component. It tracks unit counts and exposes `purchase(good_id, units, cost, budget)`, `consume(good_id)`, `available(good_id)`, `level(good_id)`. `Seller` delegates all stock operations to it.

`StockStrategy` is a `Protocol` with `__call__(seller, good_id, cost) -> int` (units to buy). Built-in implementations: `FixedStock(units=100)` and `BudgetFraction(fraction=0.05)`. Registered in `STOCK_REGISTRY` in `stock_strategies.py`. `Market.run()` accepts `pricing_strategy` and `stock_strategy`; the daily loop is: purchase → update prices → simulate.

**Padding** — sellers have shorter histories if created with a non-default `start_day`. `Seller.profit_series(n_days)` and `sales_series(good_id, n_days)` zero-pad from the left based on `start_day`. Use these methods when aggregating across sellers — never pad manually in other modules.

**visualization.py** — sets `matplotlib.use('Agg')` at import time. Not imported in `market/__init__.py` deliberately, so tests never touch matplotlib. `_smooth` uses `mode='valid'` convolution and returns an aligned x-axis to avoid zero-padding artifacts at series edges. Helpers receive `Good` objects; use `good.name` for axis labels and `good.id` for dict lookups.

## Constraints

- Sellers only observe their own sales — they do not see competitors' prices or sales
- Prices are fixed per day and updated simultaneously after each day
- Cost is fixed and identical for the same good across all sellers
- `Good.value` and `Good.lam` are hidden from sellers (they learn implicitly via sales)
- Prices are hard-floored at `cost × 1.001` in `Market._update_prices`

## Python Version

Requires Python ≥ 3.10 (uses `dict[str, ...]` and `set[str]` as type annotations).
Runtime: Python 3.12.3 (WSL).
