from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List

import numpy as np

from .goods import Good
from .stock_manager import StockManager

if TYPE_CHECKING:
    from .strategies import PricingStrategy


@dataclass
class Seller:
    name:      str
    goods:     List[str]
    budget:    float
    start_day: int = 1

    prices:         Dict[str, float]       = field(default_factory=dict)
    hist_price:     Dict[str, List[float]] = field(default_factory=dict)
    hist_sales:     Dict[str, List[int]]   = field(default_factory=dict)
    hist_profit:    Dict[str, List[float]] = field(default_factory=dict)
    hist_stock:     Dict[str, List[int]]   = field(default_factory=dict)
    hist_budget:    List[float]            = field(default_factory=list)
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
        """Purchase units of a good, registering it if new. Deducts cost from budget."""
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
        self.hist_price[name]  = []
        self.hist_sales[name]  = []
        self.hist_profit[name] = []
        self.hist_stock[name]  = []

    # ------------------------------------------------------------------
    def record(self, good: str, price: float, sales: int, profit: float) -> None:
        self.hist_price[good].append(price)
        self.hist_sales[good].append(sales)
        self.hist_profit[good].append(profit)
        self.hist_stock[good].append(self._stock_manager.level(good))
        self.budget += profit

    def record_end_of_day(self) -> None:
        self.hist_budget.append(self.budget)

    def total_profit(self) -> float:
        return sum(sum(v) for v in self.hist_profit.values())

    # ------------------------------------------------------------------
    def profit_series(self, n_days: int) -> np.ndarray:
        """Total daily profit across all goods, zero-padded for pre-entry days."""
        return sum(
            (self._padded(self.hist_profit[g], n_days) for g in self.goods),
            np.zeros(n_days),
        )

    def sales_series(self, good: str, n_days: int) -> np.ndarray:
        return self._padded(self.hist_sales[good], n_days)

    def _padded(self, hist: List, n_days: int) -> np.ndarray:
        arr = [0] * (self.start_day - 1) + list(hist)
        return np.array((arr + [0] * n_days)[:n_days], dtype=float)
