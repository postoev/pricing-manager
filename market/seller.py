from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List

import numpy as np

from .goods import Good
from .metrics import GoodMetrics, SellerMetrics
from .stock_manager import StockManager

if TYPE_CHECKING:
    from .pricing_strategies import PricingStrategy


@dataclass
class Seller:
    name:      str
    goods:     List[str]
    budget:    float
    start_day: int = 1

    prices:         Dict[str, float]       = field(default_factory=dict)
    good_metrics:   Dict[str, GoodMetrics] = field(default_factory=dict)
    seller_metrics: SellerMetrics          = field(default_factory=SellerMetrics)
    _stock_manager: StockManager           = field(default_factory=StockManager)

    # ------------------------------------------------------------------
    def setup(self, goods: Dict[str, Good]) -> None:
        for g in self.goods:
            self._init_good(g, goods[g].cost * 2.0)

    def add_good(self, good_name: str, good: Good) -> None:
        if good_name not in self.goods:
            self.goods.append(good_name)
        self._init_good(good_name, good.cost * 2.0)

    def update_prices(self, strategy: PricingStrategy, costs: Dict[str, float]) -> None:
        for g in self.goods:
            cost = costs[g]
            self.prices[g] = max(strategy(self, g, cost), cost * 1.001)

    def purchase_stock(self, good_name: str, units: int, good: Good) -> None:
        if good_name not in self.goods:
            self.goods.append(good_name)
            self._init_good(good_name, good.cost * 2.0)
        bought, cost = self._stock_manager.purchase(good_name, units, good.cost, self.budget)
        self.budget -= cost

    def has_stock(self, good_name: str) -> bool:
        return self._stock_manager.available(good_name)

    def consume_stock(self, good_name: str) -> None:
        self._stock_manager.consume(good_name)

    def stock_level(self, good_name: str) -> int:
        return self._stock_manager.level(good_name)

    def _init_good(self, name: str, initial_price: float) -> None:
        self.prices[name]      = initial_price
        self.good_metrics[name] = GoodMetrics(start_day=self.start_day)

    # ------------------------------------------------------------------
    def record(self, good: str, price: float, sales: int, profit: float) -> None:
        self.good_metrics[good].record(price, sales, profit, self._stock_manager.level(good))
        self.budget += profit

    def record_end_of_day(self) -> None:
        self.seller_metrics.record(self.budget)

    def total_profit(self) -> float:
        return sum(sum(m.profit) for m in self.good_metrics.values())

    # ------------------------------------------------------------------
    def profit_series(self, n_days: int) -> np.ndarray:
        return sum(
            (m.profit_series(n_days) for m in self.good_metrics.values()),
            np.zeros(n_days),
        )

    def sales_series(self, good: str, n_days: int) -> np.ndarray:
        return self.good_metrics[good].sales_series(n_days)
