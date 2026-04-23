from __future__ import annotations
import random
from pathlib import Path
from typing import List, Optional

import numpy as np

from .assortment import Assortment
from . import catalog
from .seller import Seller
from .simulation import Market


def build_market(
    n_goods:        int,
    n_sellers:      int,
    buyers_per_day: int,
    seed:           Optional[int] = 42,
    catalog_path:   Path = catalog.DEFAULT_PATH,
) -> Market:
    rng = np.random.default_rng(seed)
    if seed is not None:
        random.seed(seed)

    assortment = _make_assortment(n_goods, rng, catalog_path)
    sellers    = _make_sellers(n_sellers, rng)
    return Market(assortment, sellers, buyers_per_day)


# ---------------------------------------------------------------------------

def _make_assortment(n: int, rng: np.random.Generator, path: Path) -> Assortment:
    if catalog.is_initialized(path):
        goods = catalog.load(path)[:n]
    else:
        goods = catalog.generate(n, rng)
        catalog.save(goods, path)

    assortment = Assortment()
    for g in goods:
        assortment.add(g)
    return assortment


def _make_sellers(n: int, rng: np.random.Generator) -> List[Seller]:
    return [Seller(name=f"S{j + 1}", goods=[], budget=10_000.0) for j in range(n)]
