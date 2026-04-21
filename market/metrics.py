from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

import numpy as np


def _padded(hist: List, n_days: int, start_day: int) -> np.ndarray:
    arr = [0] * (start_day - 1) + list(hist)
    return np.array((arr + [0] * n_days)[:n_days], dtype=float)


@dataclass
class GoodMetrics:
    """Tracks one seller's trading history for one good."""
    start_day: int = 1
    prices: List[float] = field(default_factory=list)
    sales:  List[int]   = field(default_factory=list)
    profit: List[float] = field(default_factory=list)
    stock:  List[int]   = field(default_factory=list)

    def record(self, price: float, sales: int, profit: float, stock: int) -> None:
        self.prices.append(price)
        self.sales.append(sales)
        self.profit.append(profit)
        self.stock.append(stock)

    def price_series(self, n_days: int) -> np.ndarray:
        return _padded(self.prices, n_days, self.start_day)

    def sales_series(self, n_days: int) -> np.ndarray:
        return _padded(self.sales, n_days, self.start_day)

    def profit_series(self, n_days: int) -> np.ndarray:
        return _padded(self.profit, n_days, self.start_day)


@dataclass
class SellerMetrics:
    """Tracks seller-level history (budget)."""
    start_day: int = 1
    budget: List[float] = field(default_factory=list)

    def record(self, budget: float) -> None:
        self.budget.append(budget)

    def budget_series(self, n_days: int) -> np.ndarray:
        return _padded(self.budget, n_days, self.start_day)
