from __future__ import annotations
import random
from typing import List

from .assortment import Assortment
from .seller import Seller
from .strategies import PricingStrategy
from .stock_strategies import StockStrategy


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

        for s in sellers:
            s.setup({g: goods[g] for g in s.goods})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        n_days:         int,
        pricing_strategy: PricingStrategy,
        stock_strategy:   StockStrategy,
        verbose:          bool = True,
    ) -> None:
        for d in range(n_days):
            self._purchase_stock(stock_strategy)
            self._update_prices(pricing_strategy)
            self._simulate_day()
            if verbose and (d % max(1, n_days // 10) == 0 or d == n_days - 1):
                self._print_day()

    # ------------------------------------------------------------------
    # Simulation internals
    # ------------------------------------------------------------------

    def _purchase_stock(self, stock_strategy: StockStrategy) -> None:
        for seller in self.sellers:
            for good_name, good in self.goods.items():
                units = stock_strategy(seller, good_name, good.cost)
                if units > 0:
                    seller.purchase_stock(good_name, units, good)

    def _simulate_day(self) -> None:
        self.day += 1

        good_names = self.goods.names()
        day_sales  = {s.name: {g: 0   for g in s.goods} for s in self.sellers}
        day_profit = {s.name: {g: 0.0 for g in s.goods} for s in self.sellers}

        for _ in range(self.buyers_per_day):
            good_name = random.choice(good_names)
            available = [s for s in self.sellers if s.has_stock(good_name)]
            if not available:
                continue

            good    = self.goods[good_name]
            logits  = [good.logit(s.prices[good_name]) for s in available]
            outcome = random.choices(range(-1, len(available)),
                                     weights=[1.0] + logits, k=1)[0]
            if outcome >= 0:
                seller = available[outcome]
                seller.consume_stock(good_name)
                price  = seller.prices[good_name]
                day_sales [seller.name][good_name] += 1
                day_profit[seller.name][good_name] += price - good.cost

        for s in self.sellers:
            for g in s.goods:
                s.record(g, s.prices[g],
                         day_sales[s.name][g],
                         day_profit[s.name][g])
            s.record_end_of_day()

    def _update_prices(self, pricing_strategy: PricingStrategy) -> None:
        costs = {g: self.goods[g].cost for g in self.goods}
        for s in self.sellers:
            s.update_prices(pricing_strategy, costs)

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
                      f"profit={s.hist_profit[g][-1]:.1f}, "
                      f"stock={s.stock_level(g)}")
