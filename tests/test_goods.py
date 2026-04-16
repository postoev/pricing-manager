import pytest
from market.goods import Good


@pytest.fixture
def good():
    return Good(name='G1', cost=10.0, value=30.0, lam=0.15)


def test_logit_at_value_is_one(good):
    assert good.logit(good.value) == pytest.approx(1.0)


def test_logit_strictly_decreasing_with_price(good):
    assert good.logit(10.0) > good.logit(20.0) > good.logit(30.0) > good.logit(50.0)


def test_logit_always_positive(good):
    for price in [0.0, 5.0, 30.0, 100.0, 1000.0]:
        assert good.logit(price) > 0


def test_logit_very_high_price_near_zero(good):
    assert good.logit(1000.0) < 1e-10


def test_monopoly_opt_above_cost(good):
    assert good.monopoly_optimal_price() > good.cost


def test_monopoly_opt_below_twice_value(good):
    assert good.monopoly_optimal_price() < good.value * 2


def test_monopoly_opt_increases_with_cost():
    g1 = Good('G', cost=10.0, value=30.0, lam=0.15)
    g2 = Good('G', cost=20.0, value=60.0, lam=0.15)  # scaled up proportionally
    assert g2.monopoly_optimal_price() > g1.monopoly_optimal_price()
