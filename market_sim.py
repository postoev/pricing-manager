# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "matplotlib"]
# ///
"""
Market Simulator CLI.

Examples:
    pipx run market_sim.py -n 2 -s 3 -d 60
    pipx run market_sim.py -n 1 -s 1 -d 90 --entry 30:S_new:G1
    pipx run market_sim.py -n 2 -s 2 -d 60 --entry 20:S1:G2 --strategy gradient
"""
from __future__ import annotations
import argparse

from market import build_market, REGISTRY, Event
from market.visualization import plot_simulation


def parse_entry(spec: str, known_sellers: set[str]) -> Event:
    parts = spec.split(':')
    if len(parts) != 3:
        raise ValueError(
            f"Неверный формат '{spec}', ожидается DAY:SELLER:G1[,G2,...]"
        )
    day_str, seller, goods_str = parts
    goods = [g.strip() for g in goods_str.split(',')]
    kind  = 'add_good' if seller in known_sellers else 'new_seller'
    return Event(day=int(day_str), kind=kind, seller=seller, goods=goods)


def main() -> None:
    parser = argparse.ArgumentParser(description='Market Simulator')
    parser.add_argument('-n', '--goods',    type=int, default=1)
    parser.add_argument('-s', '--sellers',  type=int, default=1)
    parser.add_argument('-c', '--buyers',   type=int, default=1000)
    parser.add_argument('-d', '--days',     type=int, default=60)
    parser.add_argument('--strategy', default='epsilon_greedy',
                        choices=list(REGISTRY))
    parser.add_argument('--no-plot', action='store_true')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--entry', action='append', default=[],
                        metavar='DAY:SELLER:G1[,G2]',
                        help='Market event (repeatable)')
    args = parser.parse_args()

    print(f"=== Market Simulator ===")
    print(f"  Goods={args.goods}  Sellers={args.sellers}  "
          f"Buyers/day={args.buyers}  Days={args.days}  "
          f"Strategy={args.strategy}")

    market   = build_market(args.goods, args.sellers, args.buyers, args.seed)
    strategy = REGISTRY[args.strategy]

    print("\n--- Setup ---")
    for gname, g in market.goods.items():
        carriers = [s.name for s in market.sellers if gname in s.goods]
        print(f"  {gname}: cost={g.cost:.2f}  value={g.value:.2f}  "
              f"lam={g.lam:.3f}  opt={g.monopoly_optimal_price():.2f}  "
              f"sellers={carriers}")

    known = {s.name for s in market.sellers}
    for spec in args.entry:
        try:
            market.schedule(parse_entry(spec, known))
        except ValueError as exc:
            print(f"[!] {exc}")

    market.run(n_days=args.days, strategy=strategy, verbose=True)

    print("\n=== Final totals ===")
    for s in market.sellers:
        print(f"  {s.name}: cumulative profit = {s.total_profit():.1f}")

    if not args.no_plot:
        plot_simulation(market)


if __name__ == '__main__':
    main()
