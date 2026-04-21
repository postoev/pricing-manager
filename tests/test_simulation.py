import random
import pytest
import numpy as np

from market.assortment       import Assortment
from market.goods            import Good
from market.seller           import Seller
from market.simulation       import Market
from market.pricing_strategies import EpsilonGreedy
from market.stock_strategies import FixedStock


def make_assortment(*goods: Good) -> Assortment:
    a = Assortment()
    for g in goods:
        a.add(g)
    return a


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def single_good():
    return Good('G1', cost=10.0, value=30.0, lam=0.15)


@pytest.fixture
def simple_market(single_good):
    sellers = [Seller(name='S1', goods=['G1'], budget=10_000.0)]
    return Market(make_assortment(single_good), sellers, buyers_per_day=500)


# ---------------------------------------------------------------------------
# Basic mechanics
# ---------------------------------------------------------------------------

def test_day_counter_increments(simple_market):
    assert simple_market.day == 0
    simple_market._simulate_day()
    assert simple_market.day == 1
    simple_market._simulate_day()
    assert simple_market.day == 2


def test_history_length_matches_days(simple_market):
    for _ in range(5):
        simple_market._simulate_day()
    assert len(simple_market.sellers[0].good_metrics['G1'].sales) == 5


def test_sales_are_non_negative(simple_market):
    for _ in range(10):
        simple_market._simulate_day()
    assert all(v >= 0 for v in simple_market.sellers[0].good_metrics['G1'].sales)


def test_run_advances_correct_number_of_days(simple_market):
    simple_market.run(
        n_days=7,
        pricing_strategy=EpsilonGreedy(),
        stock_strategy=FixedStock(),
        verbose=False,
    )
    assert simple_market.day == 7


# ---------------------------------------------------------------------------
# Demand / outside option
# ---------------------------------------------------------------------------

def test_very_high_price_yields_few_sales(single_good):
    sellers = [Seller(name='S1', goods=[], budget=10_000.0)]
    market  = Market(make_assortment(single_good), sellers, buyers_per_day=1000)
    market._purchase_stock(FixedStock(units=1000))
    sellers[0].prices['G1'] = 500.0
    market._simulate_day()
    assert sellers[0].good_metrics['G1'].sales[0] < 10


def test_lower_price_yields_more_sales(single_good):
    def sales_at_price(price, seed=0):
        random.seed(seed)
        np.random.seed(seed)
        sellers = [Seller(name='S1', goods=[], budget=10_000.0)]
        market  = Market(make_assortment(single_good), sellers, buyers_per_day=2000)
        market._purchase_stock(FixedStock(units=2000))
        sellers[0].prices['G1'] = price
        market._simulate_day()
        return sellers[0].good_metrics['G1'].sales[0]

    assert sales_at_price(15.0) > sales_at_price(50.0)


def test_competition_expands_total_market(single_good):
    def total_sales(n_sellers, seed=42):
        random.seed(seed)
        np.random.seed(seed)
        sellers = [Seller(name=f'S{i}', goods=[], budget=10_000.0) for i in range(n_sellers)]
        market  = Market(make_assortment(single_good), sellers, buyers_per_day=5000)
        market._purchase_stock(FixedStock(units=5000))
        for s in sellers:
            s.prices['G1'] = 20.0
        market._simulate_day()
        return sum(s.good_metrics['G1'].sales[0] for s in sellers)

    assert total_sales(2) > total_sales(1)


# ---------------------------------------------------------------------------
# Stock mechanics
# ---------------------------------------------------------------------------

def test_no_sales_without_stock(single_good):
    sellers = [Seller(name='S1', goods=['G1'], budget=10_000.0)]
    market  = Market(make_assortment(single_good), sellers, buyers_per_day=1000)
    market._simulate_day()
    assert sellers[0].good_metrics['G1'].sales[0] == 0


def test_stock_depletes_on_sale(single_good):
    sellers = [Seller(name='S1', goods=[], budget=10_000.0)]
    market  = Market(make_assortment(single_good), sellers, buyers_per_day=1000)
    market._purchase_stock(FixedStock(units=5))
    sellers[0].prices['G1'] = 15.0
    market._simulate_day()
    assert sellers[0].stock_level('G1') < 5


def test_purchase_stock_registers_new_good(single_good):
    seller = Seller(name='S1', goods=[], budget=10_000.0)
    assert 'G1' not in seller.goods
    seller.purchase_stock('G1', 10, single_good)
    assert 'G1' in seller.goods
    assert seller.stock_level('G1') == 10


def test_purchase_stock_deducts_budget(single_good):
    seller = Seller(name='S1', goods=[], budget=10_000.0)
    seller.purchase_stock('G1', 100, single_good)
    assert seller.budget == pytest.approx(10_000.0 - 100 * single_good.cost)
