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

## Interactive Notebook

`market_sim.ipynb` provides a step-by-step interactive interface powered by `ipywidgets`:

```bash
jupyter notebook market_sim.ipynb
```

Features:
- Configure goods, sellers, buyers, strategy, and seed via form controls
- Advance the simulation **+1 day**, **+10 days**, or any arbitrary N
- Live metrics table: cumulative profit, today's profit and sales, current prices vs. monopoly optimum
- Live charts: price dynamics, market share, cumulative and daily profit — updated after every step

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `-n`, `--goods` | 1 | Number of goods |
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

## Tests

```bash
pipx run run_tests.py
```

34 tests across goods, seller, strategies, and simulation mechanics.

## Project Structure

```
market/
├── goods.py          # Good dataclass — logit(), monopoly_optimal_price()
├── assortment.py     # Assortment — container and aggregator for all market goods
├── seller.py         # Seller dataclass — budget, history, padding helpers
├── strategies.py     # Strategy protocol, EpsilonGreedy, GradientAscent, REGISTRY
├── simulation.py     # Market — simulate_day, price updates
├── factory.py        # build_market — random market generation
└── visualization.py  # plot_simulation — matplotlib charts, edge-safe smoothing

market_sim.py         # CLI entry point
market_sim.ipynb      # Interactive Jupyter notebook
run_tests.py          # Test runner (pipx run run_tests.py)
```

## Adding a New Pricing Strategy

1. Add a callable dataclass to `market/strategies.py`:

```python
@dataclass
class MyStrategy:
    my_param: float = 0.5

    def __call__(self, seller: Seller, good: str, cost: float) -> float:
        # cost is the lower bound for any price proposal
        ...
        return new_price
```

2. Register it:

```python
REGISTRY['my_strategy'] = MyStrategy()
```

3. Use it:

```bash
pipx run market_sim.py --strategy my_strategy
```
