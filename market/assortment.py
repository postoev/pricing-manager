from __future__ import annotations
from typing import Dict, Iterator

from .goods import Good


class Assortment:
    """All goods available on the market — add, look up, and inspect."""

    def __init__(self) -> None:
        self._goods: Dict[str, Good] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(self, good: Good) -> None:
        self._goods[good.name] = good

    # ------------------------------------------------------------------
    # Mapping-like access (read-only)
    # ------------------------------------------------------------------

    def __getitem__(self, name: str) -> Good:
        return self._goods[name]

    def __contains__(self, name: object) -> bool:
        return name in self._goods

    def __iter__(self) -> Iterator[str]:
        return iter(self._goods)

    def __len__(self) -> int:
        return len(self._goods)

    def __repr__(self) -> str:
        names = list(self._goods)
        return f"Assortment({names})"

    def names(self) -> list[str]:
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
        return {name: g.monopoly_optimal_price() for name, g in self._goods.items()}

    def summary(self) -> None:
        print(f"Assortment: {len(self)} goods")
        for name, g in self._goods.items():
            print(f"  {name}: cost={g.cost:.2f}, "
                  f"value={g.value:.2f}, "
                  f"opt≈{g.monopoly_optimal_price():.2f}")
