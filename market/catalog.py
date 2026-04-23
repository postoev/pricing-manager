from __future__ import annotations
import csv
import uuid
from pathlib import Path
from typing import List

from .goods import Good

DEFAULT_PATH = Path(__file__).parent.parent / "data" / "assortment.csv"

_FIELDS = ["id", "name", "description", "cost", "value", "lam"]

# 50 base products across categories
_BASE_PRODUCTS: list[dict] = [
    {"name": "Bread",             "base_cost": 12.0},
    {"name": "Milk",              "base_cost": 18.0},
    {"name": "Eggs",              "base_cost": 22.0},
    {"name": "Butter",            "base_cost": 28.0},
    {"name": "Coffee",            "base_cost": 35.0},
    {"name": "Shampoo",           "base_cost": 42.0},
    {"name": "Toothpaste",        "base_cost": 30.0},
    {"name": "Rice",              "base_cost": 25.0},
    {"name": "Pasta",             "base_cost": 20.0},
    {"name": "Olive Oil",         "base_cost": 55.0},
    {"name": "Orange Juice",      "base_cost": 38.0},
    {"name": "Yogurt",            "base_cost": 32.0},
    {"name": "Cheese",            "base_cost": 60.0},
    {"name": "Soap",              "base_cost": 15.0},
    {"name": "Chips",             "base_cost": 24.0},
    {"name": "Chocolate",         "base_cost": 48.0},
    {"name": "Honey",             "base_cost": 65.0},
    {"name": "Sugar",             "base_cost": 16.0},
    {"name": "Green Tea",         "base_cost": 45.0},
    {"name": "Laundry Detergent", "base_cost": 78.0},
    {"name": "Flour",             "base_cost": 14.0},
    {"name": "Salt",              "base_cost":  8.0},
    {"name": "Vinegar",           "base_cost": 10.0},
    {"name": "Canned Tomatoes",   "base_cost": 20.0},
    {"name": "Canned Beans",      "base_cost": 18.0},
    {"name": "Black Tea",         "base_cost": 30.0},
    {"name": "Mineral Water",     "base_cost": 12.0},
    {"name": "Apple Juice",       "base_cost": 32.0},
    {"name": "Energy Drink",      "base_cost": 55.0},
    {"name": "Cream",             "base_cost": 35.0},
    {"name": "Sour Cream",        "base_cost": 28.0},
    {"name": "Kefir",             "base_cost": 22.0},
    {"name": "Cottage Cheese",    "base_cost": 38.0},
    {"name": "Cookies",           "base_cost": 30.0},
    {"name": "Crackers",          "base_cost": 22.0},
    {"name": "Almonds",           "base_cost": 70.0},
    {"name": "Body Lotion",       "base_cost": 50.0},
    {"name": "Deodorant",         "base_cost": 45.0},
    {"name": "Conditioner",       "base_cost": 40.0},
    {"name": "Face Cream",        "base_cost": 80.0},
    {"name": "Hand Cream",        "base_cost": 35.0},
    {"name": "Shower Gel",        "base_cost": 38.0},
    {"name": "Dish Soap",         "base_cost": 25.0},
    {"name": "Sponge",            "base_cost": 12.0},
    {"name": "Trash Bags",        "base_cost": 30.0},
    {"name": "Toilet Paper",      "base_cost": 20.0},
    {"name": "Paper Towels",      "base_cost": 25.0},
    {"name": "Aluminum Foil",     "base_cost": 18.0},
    {"name": "Sunscreen",         "base_cost": 75.0},
    {"name": "Vitamin C",         "base_cost": 45.0},
]

_SIZES: list[dict] = [
    {"label": "Mini",       "cost_mult": 0.50},
    {"label": "Standard",   "cost_mult": 1.00},
    {"label": "Large",      "cost_mult": 1.80},
    {"label": "Value Pack", "cost_mult": 3.20},
    {"label": "Bulk",       "cost_mult": 5.50},
]

_QUALITIES: list[dict] = [
    {"label": "Budget",  "cost_mult": 0.70},
    {"label": "Classic", "cost_mult": 1.00},
    {"label": "Premium", "cost_mult": 1.60},
    {"label": "Organic", "cost_mult": 2.20},
]

# Products vary fastest → first n goods span all 50 product types before repeating sizes/qualities
_ALL_COMBOS: list[dict] = [
    {
        "name": f"{p['name']} {s['label']} {q['label']}",
        "description": f"{q['label']} {p['name'].lower()}, {s['label'].lower()} size",
        "cost": round(p["base_cost"] * s["cost_mult"] * q["cost_mult"], 2),
    }
    for s in _SIZES
    for q in _QUALITIES
    for p in _BASE_PRODUCTS
]

MAX_GOODS = len(_ALL_COMBOS)  # 1000


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
    if n > MAX_GOODS:
        raise ValueError(f"catalog supports at most {MAX_GOODS} goods, requested {n}")
    return [
        Good(
            id=str(uuid.uuid4()),
            name=combo["name"],
            description=combo["description"],
            cost=combo["cost"],
            value=round(combo["cost"] * float(rng.uniform(2.5, 4.0)), 2),
            lam=round(float(rng.uniform(0.10, 0.20)), 4),
        )
        for combo in _ALL_COMBOS[:n]
    ]
