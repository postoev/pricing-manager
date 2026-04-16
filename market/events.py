from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(order=True)
class Event:
    """
    A scheduled market-structure change.

    kind='new_seller' : a new seller enters with the listed goods
    kind='add_good'   : an existing seller expands their assortment
    """
    day:    int
    kind:   str        # 'new_seller' | 'add_good'
    seller: str
    goods:  List[str]
