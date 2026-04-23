import pytest
from market.goods import Good
from market.seller import Seller
from market.stock_strategies import (
    FixedStock, BudgetFraction, STOCK_REGISTRY, StockStrategy,
)


@pytest.fixture
def seller():
    g = Good(id='G1', name='Bread', cost=10.0, value=30.0, lam=0.15)
    s = Seller(name='S1', goods=['G1'], budget=1_000.0)
    s.setup({'G1': g})
    return s


def test_fixed_stock_always_returns_set_units(seller):
    strategy = FixedStock(units=50)
    assert strategy(seller, 'G1', cost=10.0) == 50


def test_fixed_stock_independent_of_budget(seller):
    seller.budget = 1.0
    assert FixedStock(units=50)(seller, 'G1', cost=10.0) == 50


def test_budget_fraction_proportional_to_budget(seller):
    units = BudgetFraction(fraction=0.1)(seller, 'G1', cost=10.0)
    assert units == 10  # int(1000 * 0.1 / 10)


def test_budget_fraction_zero_budget_returns_zero(seller):
    seller.budget = 0.0
    assert BudgetFraction()(seller, 'G1', cost=10.0) == 0


def test_budget_fraction_decreases_as_budget_drops(seller):
    high = BudgetFraction(fraction=0.1)(seller, 'G1', cost=10.0)
    seller.budget = 100.0
    low  = BudgetFraction(fraction=0.1)(seller, 'G1', cost=10.0)
    assert high > low


def test_strategies_satisfy_stock_strategy_protocol():
    for strategy in [FixedStock(), BudgetFraction()]:
        assert isinstance(strategy, StockStrategy)


def test_stock_registry_has_expected_keys():
    assert set(STOCK_REGISTRY) == {'fixed', 'budget_fraction'}


def test_stock_registry_values_satisfy_protocol():
    for strategy in STOCK_REGISTRY.values():
        assert isinstance(strategy, StockStrategy)
