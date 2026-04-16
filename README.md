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

# Monopoly broken on day 30 by a new entrant
pipx run market_sim.py -n 1 -s 1 -d 60 --entry "30:S_new:G1"

# Existing seller S1 expands assortment on day 20
pipx run market_sim.py -n 2 -s 2 -d 60 --entry "20:S1:G2"

# Multiple events
pipx run market_sim.py -n 2 -s 2 -d 90 --entry "20:S_new:G1" --entry "50:S1:G2"
```

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `-n`, `--goods` | 1 | Number of goods |
| `-s`, `--sellers` | 1 | Number of sellers |
| `-c`, `--buyers` | 1000 | Buyers per day |
| `-d`, `--days` | 60 | Days to simulate |
| `--strategy` | `epsilon_greedy` | `epsilon_greedy` or `gradient` |
| `--seed` | 42 | Random seed |
| `--entry` | — | Market event (repeatable, see below) |
| `--no-plot` | — | Skip chart output |

### `--entry` format

```
DAY:SELLER_NAME:G1[,G2,...]
```

- If `SELLER_NAME` matches an existing seller → `add_good` event  
- Otherwise → `new_seller` event

## Tests

```bash
pipx run run_tests.py
```

36 tests across goods, seller, strategies, and simulation mechanics.

## Project Structure

```
market/
├── goods.py          # Good dataclass — logit(), monopoly_optimal_price()
├── seller.py         # Seller dataclass — history, padding helpers
├── events.py         # Event dataclass
├── strategies.py     # Strategy protocol, EpsilonGreedy, GradientAscent, REGISTRY
├── simulation.py     # Market — simulate_day, event dispatch, price updates
├── factory.py        # build_market — random market generation
└── visualization.py  # plot_simulation — matplotlib charts

market_sim.py         # CLI entry point
run_tests.py          # Test runner (pipx run run_tests.py)
```

## Adding a New Pricing Strategy

1. Add a callable dataclass to `market/strategies.py`:

```python
@dataclass
class MyStrategy:
    my_param: float = 0.5

    def __call__(self, seller: Seller, good: str, cost: float) -> float:
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
