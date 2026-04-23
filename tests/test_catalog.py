import csv
import tempfile
from pathlib import Path

import numpy as np
import pytest

from market.catalog import generate, load, save, is_initialized, MAX_GOODS
from market.goods import Good


@pytest.fixture
def rng():
    return np.random.default_rng(42)


@pytest.fixture
def tmp_path_csv(tmp_path):
    return tmp_path / "assortment.csv"


# --- generate ---

def test_generate_returns_requested_count(rng):
    goods = generate(10, rng)
    assert len(goods) == 10


def test_generate_all_are_good_instances(rng):
    goods = generate(5, rng)
    assert all(isinstance(g, Good) for g in goods)


def test_generate_unique_ids(rng):
    goods = generate(50, rng)
    ids = [g.id for g in goods]
    assert len(ids) == len(set(ids))


def test_generate_unique_names(rng):
    goods = generate(MAX_GOODS, rng)
    names = [g.name for g in goods]
    assert len(names) == len(set(names))


def test_generate_prices_above_cost(rng):
    goods = generate(20, rng)
    assert all(g.value > g.cost for g in goods)


def test_generate_lam_in_range(rng):
    goods = generate(20, rng)
    assert all(0.10 <= g.lam <= 0.20 for g in goods)


def test_generate_max_goods(rng):
    goods = generate(MAX_GOODS, rng)
    assert len(goods) == MAX_GOODS


def test_generate_exceeds_max_raises(rng):
    with pytest.raises(ValueError, match=str(MAX_GOODS)):
        generate(MAX_GOODS + 1, rng)


def test_generate_diversity_at_small_n(rng):
    goods = generate(50, rng)
    names = [g.name for g in goods]
    assert len(set(names)) == 50


# --- save / load / is_initialized ---

def test_is_initialized_false_for_missing(tmp_path_csv):
    assert not is_initialized(tmp_path_csv)


def test_is_initialized_true_after_save(rng, tmp_path_csv):
    save(generate(5, rng), tmp_path_csv)
    assert is_initialized(tmp_path_csv)


def test_save_and_load_roundtrip(rng, tmp_path_csv):
    original = generate(10, rng)
    save(original, tmp_path_csv)
    loaded = load(tmp_path_csv)
    assert len(loaded) == 10
    assert [g.id for g in loaded] == [g.id for g in original]
    assert [g.name for g in loaded] == [g.name for g in original]
    assert [g.cost for g in loaded] == [g.cost for g in original]
