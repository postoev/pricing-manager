from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Good:
    """
    Product with logistic demand (MNL framework).

    True purchase prob for a single seller:  σ(λ(V − price))
      V   — willingness-to-pay midpoint (50% buy at this price, monopoly)
      λ   — price sensitivity (steepness of the logistic curve)

    Both parameters are unknown to sellers.
    """
    id:          str
    name:        str
    cost:        float
    value:       float   # V
    lam:         float   # λ
    description: str = ""

    def logit(self, price: float) -> float:
        """MNL weight exp(λ(V−p)) for one seller option."""
        return float(np.exp(np.clip(self.lam * (self.value - price), -500, 500)))

    def monopoly_optimal_price(self) -> float:
        """Numerical argmax of expected profit (p−c)·σ(λ(V−p))."""
        prices = np.linspace(self.cost * 1.001, self.value * 4, 2000)
        sigma  = 1.0 / (1.0 + np.exp(self.lam * (prices - self.value)))
        return float(prices[np.argmax((prices - self.cost) * sigma)])
