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
    goods:     List[str]   # good IDs
    budget:    float
    start_day: int = 1

    prices:         Dict[str, float]       = field(default_factory=dict)
    good_metrics:   Dict[str, GoodMetrics] = field(default_factory=dict)
    seller_metrics: SellerMetrics          = field(default_factory=SellerMetrics)
    _stock_manager: StockManager           = field(default_factory=StockManager)

    # ------------------------------------------------------------------
    def setup(self, goods: Dict[str, Good]) -> None:
        for good_id in self.goods:
            self._init_good(good_id, goods[good_id].cost * 2.0)

    def add_good(self, good_id: str, good: Good) -> None:
        if good_id not in self.goods:
            self.goods.append(good_id)
        self._init_good(good_id, good.cost * 2.0)

    def update_prices(self, strategy: PricingStrategy, costs: Dict[str, float]) -> None:
        for good_id in self.goods:
            cost = costs[good_id]
            self.prices[good_id] = max(strategy(self, good_id, cost), cost * 1.001)

    def purchase_stock(self, good_id: str, units: int, good: Good) -> None:
        if good_id not in self.goods:
            self.goods.append(good_id)
            self._init_good(good_id, good.cost * 2.0)
        bought, cost = self._stock_manager.purchase(good_id, units, good.cost, self.budget)
        self.budget -= cost

    def has_stock(self, good_id: str) -> bool:
        return self._stock_manager.available(good_id)

    def consume_stock(self, good_id: str) -> None:
        self._stock_manager.consume(good_id)

    def stock_level(self, good_id: str) -> int:
        return self._stock_manager.level(good_id)

    def _init_good(self, good_id: str, initial_price: float) -> None:
        self.prices[good_id]       = initial_price
        self.good_metrics[good_id] = GoodMetrics(start_day=self.start_day)

    # ------------------------------------------------------------------
    def record(self, good_id: str, price: float, sales: int, profit: float) -> None:
        self.good_metrics[good_id].record(price, sales, profit, self._stock_manager.level(good_id))
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

    def sales_series(self, good_id: str, n_days: int) -> np.ndarray:
        return self.good_metrics[good_id].sales_series(n_days)
