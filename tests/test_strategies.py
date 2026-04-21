import pytest
from market.goods import Good
from market.seller import Seller
from market.pricing_strategies import EpsilonGreedy, GradientAscent, PRICING_REGISTRY, PricingStrategy


@pytest.fixture
def seller_with_history():
    g = Good('G1', 10.0, 30.0, 0.15)
    s = Seller(name='S1', goods=['G1'], budget=10_000.0)
    s.setup({'G1': g})
    s.record('G1', price=18.0, sales=50, profit=400.0)
    s.record('G1', price=20.0, sales=45, profit=450.0)
    s.record('G1', price=22.0, sales=40, profit=480.0)
    s.prices['G1'] = 22.0
    return s


@pytest.mark.parametrize('strategy', [EpsilonGreedy(), GradientAscent()])
def test_price_always_returned(strategy, seller_with_history):
    price = strategy(seller_with_history, 'G1', cost=10.0)
    assert isinstance(price, float)


@pytest.mark.parametrize('strategy', [
    EpsilonGreedy(epsilon=0.0),   # pure exploit
    GradientAscent(explore_prob=0.0),
])
def test_price_above_cost_on_exploit(strategy, seller_with_history):
    for _ in range(30):
        price = strategy(seller_with_history, 'G1', cost=10.0)
        assert price > 10.0


@pytest.mark.parametrize('strategy', [
    EpsilonGreedy(epsilon=1.0),   # pure explore
    GradientAscent(explore_prob=1.0),
])
def test_price_positive_on_full_explore(strategy, seller_with_history):
    for _ in range(30):
        price = strategy(seller_with_history, 'G1', cost=10.0)
        assert price > 0


def test_epsilon_greedy_explores_with_no_history():
    g = Good('G1', 10.0, 30.0, 0.15)
    s = Seller(name='S1', goods=['G1'], budget=10_000.0)
    s.setup({'G1': g})
    # no records yet → falls back to explore regardless of epsilon
    price = EpsilonGreedy(epsilon=0.0)(s, 'G1', 10.0)
    assert price > 0


def test_registry_has_expected_keys():
    assert set(PRICING_REGISTRY) == {'epsilon_greedy', 'gradient'}


def test_registry_values_satisfy_strategy_protocol():
    for strategy in PRICING_REGISTRY.values():
        assert isinstance(strategy, PricingStrategy)
