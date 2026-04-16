from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from .seller import Seller


@runtime_checkable
class Strategy(Protocol):
    """Callable that proposes a new price for one (seller, good) pair."""
    def __call__(self, seller: Seller, good: str, cost: float) -> float: ...


# ---------------------------------------------------------------------------

@dataclass
class EpsilonGreedy:
    """
    Exploit: continue in the direction that last improved profit.
    Explore: random ±explore_range perturbation with probability epsilon.
    """
    epsilon:       float = 0.25
    step:          float = 0.07
    explore_range: float = 0.15

    def __call__(self, seller: Seller, good: str, cost: float) -> float:
        cur  = seller.prices[good]
        hist = seller.hist_profit[good]

        if random.random() < self.epsilon or len(hist) < 2:
            return cur * random.uniform(1 - self.explore_range,
                                        1 + self.explore_range)

        dp        = hist[-1] - hist[-2]
        dv        = seller.hist_price[good][-1] - seller.hist_price[good][-2]
        direction = float(np.sign(dp * dv)) or random.choice([-1.0, 1.0])
        return cur * (1 + self.step * direction)


@dataclass
class GradientAscent:
    """
    Finite-difference gradient ascent on observed profit.
    Occasional random exploration to escape local optima.
    """
    lr:            float = 0.08
    explore_prob:  float = 0.15
    explore_range: float = 0.10

    def __call__(self, seller: Seller, good: str, cost: float) -> float:
        cur  = seller.prices[good]
        hist = seller.hist_profit[good]

        if random.random() < self.explore_prob or len(hist) < 2:
            return cur * random.uniform(1 - self.explore_range,
                                        1 + self.explore_range)

        dp = hist[-1] - hist[-2]
        dv = seller.hist_price[good][-1] - seller.hist_price[good][-2]
        if abs(dv) < 1e-9:
            return cur * random.uniform(1 - self.explore_range / 2,
                                        1 + self.explore_range / 2)
        return cur + self.lr * cur * float(np.sign(dp / dv))


# ---------------------------------------------------------------------------

REGISTRY: dict[str, Strategy] = {
    'epsilon_greedy': EpsilonGreedy(),
    'gradient':       GradientAscent(),
}
