from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class StockManager:
    """Per-seller inventory: tracks stock levels and handles purchase/consume operations."""

    _stock: Dict[str, int] = field(default_factory=dict)

    def purchase(self, good_name: str, units: int, cost: float, budget: float) -> tuple[int, float]:
        """Buy up to `units` within budget. Returns (units_bought, cost_paid)."""
        if cost <= 0 or budget <= 0:
            return 0, 0.0
        affordable = min(units, int(budget / cost))
        if affordable <= 0:
            return 0, 0.0
        self._stock[good_name] = self._stock.get(good_name, 0) + affordable
        return affordable, affordable * cost

    def consume(self, good_name: str) -> bool:
        """Decrement stock by one unit. Returns True if stock was available."""
        if self._stock.get(good_name, 0) > 0:
            self._stock[good_name] -= 1
            return True
        return False

    def available(self, good_name: str) -> bool:
        return self._stock.get(good_name, 0) > 0

    def level(self, good_name: str) -> int:
        return self._stock.get(good_name, 0)

    def available_goods(self) -> list[str]:
        return [g for g, qty in self._stock.items() if qty > 0]
