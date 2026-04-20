from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from .goods import Good


@dataclass
class Seller:
    name:      str
    goods:     List[str]
    budget:    float
    start_day: int = 1

    prices:      Dict[str, float]       = field(default_factory=dict)
    hist_price:  Dict[str, List[float]] = field(default_factory=dict)
    hist_sales:  Dict[str, List[int]]   = field(default_factory=dict)
    hist_profit: Dict[str, List[float]] = field(default_factory=dict)

    # ------------------------------------------------------------------
    def setup(self, goods: Dict[str, Good]) -> None:
        for g in self.goods:
            self._init_good(g, goods[g].cost * 2.0)

    def add_good(self, good_name: str, good: Good) -> None:
        if good_name not in self.goods:
            self.goods.append(good_name)
        self._init_good(good_name, good.cost * 2.0)

    def _init_good(self, name: str, initial_price: float) -> None:
        self.prices[name]      = initial_price
        self.hist_price[name]  = []
        self.hist_sales[name]  = []
        self.hist_profit[name] = []

    # ------------------------------------------------------------------
    def record(self, good: str, price: float, sales: int, profit: float) -> None:
        self.hist_price[good].append(price)
        self.hist_sales[good].append(sales)
        self.hist_profit[good].append(profit)
        self.budget += profit

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
