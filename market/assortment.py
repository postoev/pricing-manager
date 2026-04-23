from __future__ import annotations
from typing import Dict, Iterator

from .goods import Good


class Assortment:
    """All goods available on the market — add, look up, and inspect."""

    def __init__(self) -> None:
        self._goods: Dict[str, Good] = {}   # keyed by good.id

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(self, good: Good) -> None:
        self._goods[good.id] = good

    # ------------------------------------------------------------------
    # Mapping-like access by good ID (read-only)
    # ------------------------------------------------------------------

    def __getitem__(self, good_id: str) -> Good:
        return self._goods[good_id]

    def __contains__(self, good_id: object) -> bool:
        return good_id in self._goods

    def __iter__(self) -> Iterator[str]:
        return iter(self._goods)

    def __len__(self) -> int:
        return len(self._goods)

    def __repr__(self) -> str:
        names = [g.name for g in self._goods.values()]
        return f"Assortment({names})"

    def ids(self) -> list[str]:
        return list(self._goods)

    def items(self):
        return self._goods.items()

    def values(self):
        return self._goods.values()

    # ------------------------------------------------------------------
    # Aggregate information
    # ------------------------------------------------------------------

    def cost_range(self) -> tuple[float, float]:
        costs = [g.cost for g in self._goods.values()]
        return (min(costs), max(costs))

    def optimal_prices(self) -> dict[str, float]:
        return {good_id: g.monopoly_optimal_price() for good_id, g in self._goods.items()}

    def summary(self) -> None:
        print(f"Assortment: {len(self)} goods")
        for g in self._goods.values():
            print(f"  [{g.id}] {g.name}: cost={g.cost:.2f}, "
                  f"value={g.value:.2f}, "
                  f"opt≈{g.monopoly_optimal_price():.2f}")
