# Pricing Manager — Market Simulator

Agent-based market simulator where sellers learn optimal pricing via reinforcement learning against an unknown demand function.

## Model

**Demand** — multinomial logit (MNL):

```
P(buy from seller i) = exp(λ(V − pᵢ)) / [1 + Σⱼ exp(λ(V − pⱼ))]
```

- `V` — intrinsic value of the good (sellers don't know it)
- `λ` — price sensitivity (sellers don't know it)
- `1` in the denominator — outside option (buyer leaves without purchase)

Each day C buyers arrive. Each buyer picks a random good, then makes a single MNL draw: buy from seller i or leave. Sellers observe only their own sales and learn prices via RL heuristics.

**Monopoly optimal price** (numerical): `argmax_p (p − cost) · σ(λ(V − p))`

## Quickstart

Requires [pipx](https://pipx.pypa.io).

```bash
# Default: 1 good, 1 seller, 1000 buyers/day, 60 days
pipx run market_sim.py

# 2 goods, 3 sellers, gradient strategy
pipx run market_sim.py -n 2 -s 3 -d 90 --strategy gradient
```

On first run, `build_market` creates `data/assortment.csv` with realistic product names (Bread, Milk, Eggs, Coffee, …). Subsequent runs load goods from the same file so IDs remain stable.

## Interactive Notebook

`market_sim.ipynb` provides a step-by-step interactive interface powered by `ipywidgets`:

```bash
jupyter notebook market_sim.ipynb
```

Features:
- Configure goods, sellers, buyers, strategy, and seed via form controls
- **Step-by-step execution** — run each sub-day phase individually: Purchase → Prices → Simulate
- Advance the simulation **+1 day**, **+10 days**, or any arbitrary N days at once
- Live metrics table: cumulative profit, today's profit and sales, current prices vs. monopoly optimum
- Live charts across four tabs: seller budgets, price dynamics, market share + daily profit, stock levels

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `-n`, `--goods` | 1 | Number of goods (max 20) |
| `-s`, `--sellers` | 1 | Number of sellers |
| `-c`, `--buyers` | 1000 | Buyers per day |
| `-d`, `--days` | 60 | Days to simulate |
| `--strategy` | `epsilon_greedy` | `epsilon_greedy` or `gradient` |
| `--seed` | 42 | Random seed |
| `--no-plot` | — | Skip chart output |

## Strategies

Both strategies receive `cost` and use it as the lower bound for exploration. Prices below cost yield negative margin on every unit sold regardless of demand, so that region is never explored.

**EpsilonGreedy** — with probability `epsilon` explores a random price in `[max(cost, cur*(1−r)), cur*(1+r)]`; otherwise moves in the direction that last improved profit.

**GradientAscent** — finite-difference gradient ascent on observed profit; occasional cost-bounded random exploration to escape local optima.

## Stock Strategies

Each day, before pricing, sellers purchase inventory using a `StockStrategy`. Both built-in strategies respect the seller's budget.

**FixedStock** — buys a fixed number of units per good per day (`units=100` by default).

**BudgetFraction** — spends a fixed fraction of the seller's current budget on each good (`fraction=0.05` by default).

## Tests

```bash
pipx run run_tests.py
```

57 tests across goods, seller, metrics, strategies, stock management, and simulation mechanics.

## Project Structure

```
market/
├── goods.py              # Good dataclass — id, name, description, logit(), monopoly_optimal_price()
├── assortment.py         # Assortment — ID-keyed container for all market goods
├── catalog.py            # CSV catalog — is_initialized/load/save/generate (data/assortment.csv)
├── seller.py             # Seller dataclass — budget, prices, delegates to metrics + stock
├── metrics.py            # GoodMetrics, SellerMetrics — time-series history per entity
├── pricing_strategies.py # PricingStrategy protocol, EpsilonGreedy, GradientAscent, PRICING_REGISTRY
├── stock_manager.py      # StockManager — per-seller inventory (purchase/consume/level)
├── stock_strategies.py   # StockStrategy protocol, FixedStock, BudgetFraction, STOCK_REGISTRY
├── simulation.py         # Market — purchase → price → simulate loop
├── factory.py            # build_market — loads catalog or generates goods on first run
└── visualization.py      # plot_simulation — matplotlib charts, edge-safe smoothing

data/
└── assortment.csv        # persistent good catalog (auto-created on first run)

market_sim.py         # CLI entry point
market_sim.ipynb      # Step-by-step interactive simulator (ipywidgets)
run_tests.py          # Test runner (pipx run run_tests.py)
```

## Good Identity

`Good.id` (UUID) is the primary key everywhere: `Assortment`, `Seller.goods`, `Seller.prices`, `Seller.good_metrics`, and the CSV catalog. `Good.name` is the human-readable label used only for display. This means the same good keeps a stable ID across simulation runs as long as `data/assortment.csv` exists.

## Adding a New Pricing Strategy

1. Add a callable dataclass to `market/pricing_strategies.py`:

```python
@dataclass
class MyStrategy:
    my_param: float = 0.5

    def __call__(self, seller: Seller, good_id: str, cost: float) -> float:
        # cost is the lower bound for any price proposal
        # read history via seller.good_metrics[good_id].prices / .profit / .sales
        ...
        return new_price
```

2. Register it:

```python
PRICING_REGISTRY['my_strategy'] = MyStrategy()
```

3. Use it:

```bash
pipx run market_sim.py --strategy my_strategy
```
