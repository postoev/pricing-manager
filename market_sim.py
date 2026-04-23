# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib"]
# ///
"""
Market Simulator CLI.

Examples:
    pipx run market_sim.py -n 2 -s 3 -d 60
    pipx run market_sim.py -n 1 -s 1 -d 90
    pipx run market_sim.py -n 2 -s 2 -d 60 --strategy gradient
"""
from __future__ import annotations
import argparse

from market import build_market, PRICING_REGISTRY
from market.visualization import plot_simulation


def main() -> None:
    parser = argparse.ArgumentParser(description='Market Simulator')
    parser.add_argument('-n', '--goods',    type=int, default=1)
    parser.add_argument('-s', '--sellers',  type=int, default=1)
    parser.add_argument('-c', '--buyers',   type=int, default=1000)
    parser.add_argument('-d', '--days',     type=int, default=60)
    parser.add_argument('--strategy', default='epsilon_greedy',
                        choices=list(PRICING_REGISTRY))
    parser.add_argument('--no-plot', action='store_true')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    print(f"=== Market Simulator ===")
    print(f"  Goods={args.goods}  Sellers={args.sellers}  "
          f"Buyers/day={args.buyers}  Days={args.days}  "
          f"Strategy={args.strategy}")

    market           = build_market(args.goods, args.sellers, args.buyers, args.seed)
    pricing_strategy = PRICING_REGISTRY[args.strategy]

    print("\n--- Setup ---")
    for good_id, g in market.goods.items():
        carriers = [s.name for s in market.sellers if good_id in s.goods]
        print(f"  {g.name}: cost={g.cost:.2f}  value={g.value:.2f}  "
              f"lam={g.lam:.3f}  opt={g.monopoly_optimal_price():.2f}  "
              f"sellers={carriers}")

    market.run(n_days=args.days, pricing_strategy=pricing_strategy, verbose=True)

    print("\n=== Final totals ===")
    for s in market.sellers:
        print(f"  {s.name}: cumulative profit = {s.total_profit():.1f}")

    if not args.no_plot:
        plot_simulation(market)


if __name__ == '__main__':
    main()
