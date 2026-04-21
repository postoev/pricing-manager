import pytest
import numpy as np
from market.goods import Good
from market.seller import Seller


@pytest.fixture
def good():
    return Good(name='G1', cost=10.0, value=30.0, lam=0.15)


@pytest.fixture
def seller(good):
    s = Seller(name='S1', goods=['G1'], budget=10_000.0)
    s.setup({'G1': good})
    return s


def test_setup_price_is_twice_cost(seller, good):
    assert seller.prices['G1'] == pytest.approx(good.cost * 2.0)


def test_setup_histories_are_empty(seller):
    assert seller.good_metrics['G1'].sales  == []
    assert seller.good_metrics['G1'].profit == []
    assert seller.good_metrics['G1'].prices == []


def test_record_appends_to_all_histories(seller):
    seller.record('G1', price=20.0, sales=50, profit=500.0)
    assert seller.good_metrics['G1'].prices == [20.0]
    assert seller.good_metrics['G1'].sales  == [50]
    assert seller.good_metrics['G1'].profit == [500.0]


def test_total_profit_sums_across_days(seller):
    seller.record('G1', 20.0, 10, 100.0)
    seller.record('G1', 22.0, 12, 144.0)
    assert seller.total_profit() == pytest.approx(244.0)


def test_total_profit_sums_across_goods(good):
    g2 = Good('G2', 15.0, 40.0, 0.12)
    s  = Seller(name='S1', goods=['G1', 'G2'], budget=10_000.0)
    s.setup({'G1': good, 'G2': g2})
    s.record('G1', 20.0, 5, 50.0)
    s.record('G2', 30.0, 3, 45.0)
    assert s.total_profit() == pytest.approx(95.0)


def test_add_good_initialises_correctly(good):
    s = Seller(name='S1', goods=[], budget=10_000.0)
    s.add_good('G1', good)
    assert 'G1' in s.goods
    assert s.prices['G1'] == pytest.approx(good.cost * 2.0)
    assert s.good_metrics['G1'].sales == []


def test_profit_series_pads_leading_zeros():
    g = Good('G1', 10.0, 30.0, 0.15)
    s = Seller(name='S1', goods=['G1'], budget=10_000.0, start_day=3)
    s.setup({'G1': g})
    s.record('G1', 20.0, 5, 50.0)
    s.record('G1', 22.0, 6, 66.0)
    assert list(s.profit_series(n_days=5)) == [0.0, 0.0, 50.0, 66.0, 0.0]


def test_sales_series_pads_leading_zeros():
    g = Good('G1', 10.0, 30.0, 0.15)
    s = Seller(name='S1', goods=['G1'], budget=10_000.0, start_day=2)
    s.setup({'G1': g})
    s.record('G1', 20.0, 10, 100.0)
    assert list(s.sales_series('G1', n_days=4)) == [0.0, 10.0, 0.0, 0.0]


def test_budget_increases_on_profit(seller):
    seller.record('G1', price=20.0, sales=10, profit=100.0)
    assert seller.budget == pytest.approx(10_100.0)


def test_budget_decreases_on_loss(seller):
    seller.record('G1', price=5.0, sales=10, profit=-50.0)
    assert seller.budget == pytest.approx(9_950.0)


def test_budget_accumulates_across_days(seller):
    seller.record('G1', 20.0, 10, 100.0)
    seller.record('G1', 22.0, 12, 144.0)
    assert seller.budget == pytest.approx(10_244.0)
