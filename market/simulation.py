from __future__ import annotations
import random
from typing import Dict, List

from .assortment import Assortment
from .seller import Seller
from .strategies import Strategy


class Market:
    def __init__(
        self,
        goods:          Assortment,
        sellers:        List[Seller],
        buyers_per_day: int = 1000,
    ) -> None:
        self.goods          = goods
        self.sellers        = sellers
        self.buyers_per_day = buyers_per_day
        self.day            = 0

        self._good_sellers: Dict[str, List[Seller]] = {g: [] for g in goods.names()}
        for s in sellers:
            for g in s.goods:
                self._good_sellers[g].append(s)

        for s in sellers:
            s.setup(goods)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, n_days: int, strategy: Strategy,
            verbose: bool = True) -> None:
        for d in range(n_days):
            self._simulate_day()
            if d < n_days - 1:
                self._update_prices(strategy)
            if verbose and (d % max(1, n_days // 10) == 0 or d == n_days - 1):
                self._print_day()

    # ------------------------------------------------------------------
    # Simulation internals
    # ------------------------------------------------------------------

    def _simulate_day(self) -> None:
        self.day += 1

        good_names = self.goods.names()
        day_sales  = {s.name: {g: 0   for g in s.goods} for s in self.sellers}
        day_profit = {s.name: {g: 0.0 for g in s.goods} for s in self.sellers}

        for _ in range(self.buyers_per_day):
            good_name = random.choice(good_names)
            available = self._good_sellers[good_name]
            if not available:
                continue

            good    = self.goods[good_name]
            logits  = [good.logit(s.prices[good_name]) for s in available]
            outcome = random.choices(range(-1, len(available)),
                                     weights=[1.0] + logits, k=1)[0]
            if outcome >= 0:
                seller = available[outcome]
                price  = seller.prices[good_name]
                day_sales [seller.name][good_name] += 1
                day_profit[seller.name][good_name] += price - good.cost

        for s in self.sellers:
            for g in s.goods:
                s.record(g, s.prices[g],
                         day_sales[s.name][g],
                         day_profit[s.name][g])

    def _update_prices(self, strategy: Strategy) -> None:
        for s in self.sellers:
            s.prices = {
                g: max(strategy(s, g, self.goods[g].cost),
                       self.goods[g].cost * 1.001)
                for g in s.goods
            }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def _print_day(self) -> None:
        print(f"\n--- Day {self.day} ---")
        for s in self.sellers:
            for g in s.goods:
                good = self.goods[g]
                print(f"  {s.name} | {g}: "
                      f"price={s.prices[g]:.2f} "
                      f"(cost={good.cost:.2f}, opt≈{good.monopoly_optimal_price():.2f}), "
                      f"sales={s.hist_sales[g][-1]}, "
                      f"profit={s.hist_profit[g][-1]:.1f}")
