from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .seller import Seller


@runtime_checkable
class StockStrategy(Protocol):
    """Callable that proposes how many units of a good a seller should purchase."""
    def __call__(self, seller: Seller, good: str, cost: float) -> int: ...


@dataclass
class FixedStock:
    """Purchase a fixed number of units of each good every day."""
    units: int = 100

    def __call__(self, seller: Seller, good: str, cost: float) -> int:
        return self.units


@dataclass
class BudgetFraction:
    """Spend `fraction` of current budget on each good per day."""
    fraction: float = 0.05

    def __call__(self, seller: Seller, good: str, cost: float) -> int:
        if seller.budget <= 0 or cost <= 0:
            return 0
        return max(0, int(seller.budget * self.fraction / cost))


STOCK_REGISTRY: dict[str, StockStrategy] = {
    'fixed':           FixedStock(),
    'budget_fraction': BudgetFraction(),
}
