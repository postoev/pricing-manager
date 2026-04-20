import pytest
from market.stock_manager import StockManager


@pytest.fixture
def mgr():
    return StockManager()


def test_purchase_returns_correct_units_and_cost(mgr):
    bought, cost = mgr.purchase('G1', units=10, cost=5.0, budget=100.0)
    assert bought == 10
    assert cost == pytest.approx(50.0)


def test_purchase_capped_by_budget(mgr):
    bought, cost = mgr.purchase('G1', units=100, cost=10.0, budget=50.0)
    assert bought == 5
    assert cost == pytest.approx(50.0)


def test_purchase_zero_budget_buys_nothing(mgr):
    bought, cost = mgr.purchase('G1', units=10, cost=5.0, budget=0.0)
    assert bought == 0
    assert cost == pytest.approx(0.0)


def test_purchase_accumulates_stock(mgr):
    mgr.purchase('G1', 10, 5.0, 1000.0)
    mgr.purchase('G1', 5,  5.0, 1000.0)
    assert mgr.level('G1') == 15


def test_consume_decrements_stock(mgr):
    mgr.purchase('G1', 3, 5.0, 100.0)
    mgr.consume('G1')
    assert mgr.level('G1') == 2


def test_consume_returns_true_when_available(mgr):
    mgr.purchase('G1', 1, 5.0, 100.0)
    assert mgr.consume('G1') is True


def test_consume_returns_false_when_empty(mgr):
    assert mgr.consume('G1') is False


def test_available_true_when_stock_positive(mgr):
    mgr.purchase('G1', 1, 5.0, 100.0)
    assert mgr.available('G1') is True


def test_available_false_when_empty(mgr):
    assert mgr.available('G1') is False


def test_level_returns_stock_count(mgr):
    mgr.purchase('G1', 7, 5.0, 100.0)
    assert mgr.level('G1') == 7


def test_available_goods_lists_nonzero(mgr):
    mgr.purchase('G1', 2, 5.0, 100.0)
    mgr.purchase('G2', 0, 5.0, 100.0)  # budget=0 effectively
    mgr.purchase('G3', 1, 5.0, 100.0)
    assert set(mgr.available_goods()) == {'G1', 'G3'}
