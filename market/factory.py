from __future__ import annotations
import random
from typing import List, Optional

import numpy as np

from .assortment import Assortment
from .goods import Good
from .seller import Seller
from .simulation import Market


def build_market(
    n_goods:        int,
    n_sellers:      int,
    buyers_per_day: int,
    seed:           Optional[int] = 42,
) -> Market:
    rng = np.random.default_rng(seed)
    if seed is not None:
        random.seed(seed)

    assortment = _make_assortment(n_goods, rng)
    sellers    = _make_sellers(n_sellers, assortment.names(), rng)
    return Market(assortment, sellers, buyers_per_day)


# ---------------------------------------------------------------------------

def _make_assortment(n: int, rng: np.random.Generator) -> Assortment:
    assortment = Assortment()
    for i in range(n):
        name = f"G{i + 1}"
        cost = round(10.0 + i * 5.0, 2)
        assortment.add(Good(
            name  = name,
            cost  = cost,
            value = round(cost * float(rng.uniform(2.5, 4.0)), 2),
            lam   = float(rng.uniform(0.10, 0.20)),
        ))
    return assortment


def _make_sellers(
    n:          int,
    good_names: List[str],
    rng:        np.random.Generator,
) -> List[Seller]:
    sets: List[set] = [set() for _ in range(n)]

    # Round-robin over shuffled goods guarantees every good has ≥1 seller.
    for idx, g in enumerate(rng.permutation(good_names)):
        sets[idx % n].add(str(g))

    # Guarantee every seller has ≥1 good (matters when n_sellers > n_goods).
    for s_set in sets:
        if not s_set:
            s_set.add(str(rng.choice(good_names)))

    # Random extras to create realistic overlap.
    for s_set in sets:
        k = int(rng.integers(0, len(good_names)))
        if k:
            for g in rng.choice(good_names, size=min(k, len(good_names)),
                                replace=False):
                s_set.add(str(g))

    return [Seller(name=f"S{j + 1}", goods=sorted(s), budget=10_000.0) for j, s in enumerate(sets)]
