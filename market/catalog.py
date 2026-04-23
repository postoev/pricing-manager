from __future__ import annotations
import csv
import uuid
from pathlib import Path
from typing import List

from .goods import Good

DEFAULT_PATH = Path(__file__).parent.parent / "data" / "assortment.csv"

_FIELDS = ["id", "name", "description", "cost", "value", "lam"]

# 20 realistic consumer goods with base costs
_PRODUCT_TEMPLATE: list[dict] = [
    {"name": "Bread",              "description": "Whole wheat bread loaf, 500g",                    "cost": 12.0},
    {"name": "Milk",               "description": "Pasteurized whole milk, 1L",                      "cost": 18.0},
    {"name": "Eggs",               "description": "Farm fresh chicken eggs, pack of 10",             "cost": 22.0},
    {"name": "Butter",             "description": "Unsalted butter block, 200g",                     "cost": 28.0},
    {"name": "Coffee",             "description": "Ground arabica coffee beans, 250g",               "cost": 35.0},
    {"name": "Shampoo",            "description": "Moisturizing shampoo for dry hair, 400ml",        "cost": 42.0},
    {"name": "Toothpaste",         "description": "Whitening fluoride toothpaste, 150ml",            "cost": 30.0},
    {"name": "Rice",               "description": "Long grain parboiled white rice, 1kg",            "cost": 25.0},
    {"name": "Pasta",              "description": "Durum wheat fusilli pasta, 500g",                 "cost": 20.0},
    {"name": "Olive Oil",          "description": "Cold-pressed extra virgin olive oil, 500ml",      "cost": 55.0},
    {"name": "Orange Juice",       "description": "100% natural squeezed orange juice, 1L",          "cost": 38.0},
    {"name": "Yogurt",             "description": "Natural Greek-style yogurt, 400g",                "cost": 32.0},
    {"name": "Cheese",             "description": "Aged Gouda cheese, 200g",                         "cost": 60.0},
    {"name": "Soap",               "description": "Antibacterial moisturizing bar soap, 100g",       "cost": 15.0},
    {"name": "Chips",              "description": "Lightly salted potato crisps, 150g",              "cost": 24.0},
    {"name": "Chocolate",          "description": "Dark chocolate 70% cacao, 100g",                  "cost": 48.0},
    {"name": "Honey",              "description": "Wildflower natural honey, 500g",                  "cost": 65.0},
    {"name": "Sugar",              "description": "Fine white granulated sugar, 1kg",                "cost": 16.0},
    {"name": "Green Tea",          "description": "Premium loose leaf green tea, 100g",              "cost": 45.0},
    {"name": "Laundry Detergent",  "description": "Concentrated bio liquid detergent, 1L",           "cost": 78.0},
]


def is_initialized(path: Path = DEFAULT_PATH) -> bool:
    return path.exists() and path.stat().st_size > 0


def load(path: Path = DEFAULT_PATH) -> List[Good]:
    with open(path, newline="", encoding="utf-8") as f:
        return [
            Good(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                cost=float(row["cost"]),
                value=float(row["value"]),
                lam=float(row["lam"]),
            )
            for row in csv.DictReader(f)
        ]


def save(goods: List[Good], path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDS)
        writer.writeheader()
        for g in goods:
            writer.writerow({
                "id": g.id, "name": g.name, "description": g.description,
                "cost": g.cost, "value": g.value, "lam": g.lam,
            })


def generate(n: int, rng) -> List[Good]:
    """Generate n goods from the built-in template using rng for value/lam."""
    if n > len(_PRODUCT_TEMPLATE):
        raise ValueError(f"catalog supports at most {len(_PRODUCT_TEMPLATE)} goods, requested {n}")
    return [
        Good(
            id=str(uuid.uuid4()),
            name=t["name"],
            description=t["description"],
            cost=t["cost"],
            value=round(t["cost"] * float(rng.uniform(2.5, 4.0)), 2),
            lam=round(float(rng.uniform(0.10, 0.20)), 4),
        )
        for t in _PRODUCT_TEMPLATE[:n]
    ]
