import math

import pytest

from src.core.bidding import MIN_DISTANCE_KM, bid, normalise_bids, rank_bids


def test_first_draft_formula():
    assert bid(2.0, 1000, 10.0) == pytest.approx(200.0)


def test_more_risk_or_population_bids_more_farther_bids_less():
    assert bid(2.0, 1000, 10.0) > bid(1.0, 1000, 10.0)
    assert bid(1.0, 2000, 10.0) > bid(1.0, 1000, 10.0)
    assert bid(1.0, 1000, 20.0) < bid(1.0, 1000, 10.0)


def test_distance_zero_is_clamped():
    assert bid(1.0, 100, 0.0) == pytest.approx(100.0 / MIN_DISTANCE_KM)
    assert bid(1.0, 100, 0.0) == bid(1.0, 100, MIN_DISTANCE_KM / 2)


@pytest.mark.parametrize("distance", [None, math.nan])
def test_distance_missing_raises(distance):
    with pytest.raises(ValueError, match="distance"):
        bid(1.0, 100, distance)


def test_population_zero_bids_zero():
    assert bid(1.0, 0, 10.0) == 0.0


@pytest.mark.parametrize("population", [None, math.nan])
def test_population_missing_raises(population):
    with pytest.raises(ValueError, match="population"):
        bid(1.0, population, 10.0)


def test_zero_risk_bids_zero():
    assert bid(0.0, 1000, 10.0) == 0.0


@pytest.mark.parametrize("args", [(-1.0, 10, 1.0), (1.0, -10, 1.0), (1.0, 10, -1.0)])
def test_negative_inputs_raise(args):
    with pytest.raises(ValueError):
        bid(*args)


def test_continuous_across_a_tier_boundary():
    # bid is a continuous function of risk: no jump either side of a boundary value
    eps = 1e-9
    assert bid(100.0 + eps, 1000, 10.0) == pytest.approx(bid(100.0 - eps, 1000, 10.0))


def test_normalise_scales_to_unit_range():
    out = normalise_bids({"A": 50.0, "B": 200.0, "C": 0.0})
    assert out == {"A": 0.25, "B": 1.0, "C": 0.0}


def test_normalise_all_zero_and_empty():
    assert normalise_bids({"A": 0.0, "B": 0.0}) == {"A": 0.0, "B": 0.0}
    assert normalise_bids({}) == {}


def test_normalise_rejects_bad_values():
    with pytest.raises(ValueError):
        normalise_bids({"A": -1.0})
    with pytest.raises(ValueError):
        normalise_bids({"A": math.nan})


def test_identical_bids_tie_break_by_name():
    ranked = rank_bids({"Talawa": 0.5, "Galnewa": 0.5, "Padaviya": 0.5})
    assert [n for n, _ in ranked] == ["Galnewa", "Padaviya", "Talawa"]


def test_rank_highest_first():
    assert rank_bids({"A": 0.1, "B": 0.9})[0] == ("B", 0.9)
