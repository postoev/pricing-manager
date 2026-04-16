import random
import pytest
import numpy as np

from market.goods      import Good
from market.seller     import Seller
from market.events     import Event
from market.simulation import Market
from market.strategies import EpsilonGreedy


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def single_good():
    return Good('G1', cost=10.0, value=30.0, lam=0.15)


@pytest.fixture
def simple_market(single_good):
    sellers = [Seller(name='S1', goods=['G1'])]
    return Market({'G1': single_good}, sellers, buyers_per_day=500)


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
    assert len(simple_market.sellers[0].hist_sales['G1']) == 5


def test_sales_are_non_negative(simple_market):
    for _ in range(10):
        simple_market._simulate_day()
    assert all(v >= 0 for v in simple_market.sellers[0].hist_sales['G1'])


def test_run_advances_correct_number_of_days(simple_market):
    simple_market.run(n_days=7, strategy=EpsilonGreedy(), verbose=False)
    assert simple_market.day == 7


# ---------------------------------------------------------------------------
# Demand / outside option
# ---------------------------------------------------------------------------

def test_very_high_price_yields_few_sales(single_good):
    sellers = [Seller(name='S1', goods=['G1'])]
    market  = Market({'G1': single_good}, sellers, buyers_per_day=1000)
    sellers[0].prices['G1'] = 500.0   # far above value=30
    market._simulate_day()
    assert sellers[0].hist_sales['G1'][0] < 10


def test_lower_price_yields_more_sales(single_good):
    """Run same seed twice at different prices; cheaper price should outsell."""
    def sales_at_price(price, seed=0):
        random.seed(seed)
        np.random.seed(seed)
        sellers = [Seller(name='S1', goods=['G1'])]
        market  = Market({'G1': single_good}, sellers, buyers_per_day=2000)
        sellers[0].prices['G1'] = price
        market._simulate_day()
        return sellers[0].hist_sales['G1'][0]

    assert sales_at_price(15.0) > sales_at_price(50.0)


def test_competition_expands_total_market(single_good):
    """MNL property: more sellers at same price → more total sales."""
    def total_sales(n_sellers, seed=42):
        random.seed(seed)
        np.random.seed(seed)
        sellers = [Seller(name=f'S{i}', goods=['G1']) for i in range(n_sellers)]
        market  = Market({'G1': single_good}, sellers, buyers_per_day=5000)
        for s in sellers:
            s.prices['G1'] = 20.0
        market._simulate_day()
        return sum(s.hist_sales['G1'][0] for s in sellers)

    assert total_sales(2) > total_sales(1)


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def test_new_seller_event_adds_seller(simple_market):
    simple_market.schedule(Event(day=3, kind='new_seller',
                                 seller='S_new', goods=['G1']))
    for _ in range(3):
        simple_market._simulate_day()
    assert any(s.name == 'S_new' for s in simple_market.sellers)


def test_new_seller_starts_recording_from_entry_day(simple_market):
    simple_market.schedule(Event(day=3, kind='new_seller',
                                 seller='S_new', goods=['G1']))
    for _ in range(5):
        simple_market._simulate_day()
    s_new = next(s for s in simple_market.sellers if s.name == 'S_new')
    assert len(s_new.hist_sales['G1']) == 3   # days 3, 4, 5
    assert s_new.start_day == 3


def test_add_good_event_expands_assortment():
    goods = {
        'G1': Good('G1', 10.0, 30.0, 0.15),
        'G2': Good('G2', 15.0, 40.0, 0.12),
    }
    sellers = [Seller('S1', ['G1']), Seller('S2', ['G2'])]
    market  = Market(goods, sellers, buyers_per_day=100)
    market.schedule(Event(day=2, kind='add_good', seller='S1', goods=['G2']))
    for _ in range(3):
        market._simulate_day()
    s1 = next(s for s in market.sellers if s.name == 'S1')
    assert 'G2' in s1.goods


def test_unknown_event_kind_does_not_crash(simple_market):
    simple_market.schedule(Event(day=1, kind='unknown_kind',
                                 seller='X', goods=['G1']))
    simple_market._simulate_day()   # should not raise


def test_event_for_unknown_seller_does_not_crash(simple_market):
    simple_market.schedule(Event(day=1, kind='add_good',
                                 seller='nonexistent', goods=['G1']))
    simple_market._simulate_day()   # should not raise
