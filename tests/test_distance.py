import dataclasses

import pytest

from saf.distance import dist, leg_cost
from saf.inputs import load_inputs
from saf.legs import Leg

PNK = (-0.150711, 109.404)
PKN = (-2.7052, 111.673)
BPN = (-1.26827, 116.894)
TRK = (3.326667, 117.569444)


@pytest.mark.parametrize(
    ("a", "b", "straight_line_km"),
    [
        # Straight-line airport distances from Project Summary.pdf, section 2.1, rounded to the km.
        (PNK, PKN, 380),
        (PKN, BPN, 602),
        (BPN, TRK, 516),
        (PNK, TRK, 986),
    ],
)
def test_distance_is_great_circle_times_road_factor(
    a: tuple[float, float], b: tuple[float, float], straight_line_km: float
) -> None:
    assert dist(*a, *b, road_factor=1.3) == pytest.approx(straight_line_km * 1.3, abs=1.0)


@pytest.mark.parametrize(
    ("leg", "usd_per_t"),
    [
        # 380 km straight line x 1.3 road factor = 494 km, at the brief's 0.10 / 0.12 / 0.08 USD per tonne-km.
        (Leg.BIOMASS_SITE_TO_DEPOT, 49.40),
        (Leg.DEPOT_TO_REFINERY, 59.28),
        (Leg.REFINERY_TO_AIRPORT, 39.52),
    ],
)
def test_leg_cost_is_rate_times_road_distance(leg: Leg, usd_per_t: float) -> None:
    params = load_inputs().parameters

    assert leg_cost(leg, *PNK, *PKN, params) == pytest.approx(usd_per_t, abs=0.1)


def test_barge_leg_uses_the_road_factor_by_default() -> None:
    params = load_inputs().parameters

    # 516 km straight line from BPN to TRK x 1.3 at 0.08 USD per tonne-km.
    assert leg_cost(Leg.REFINERY_TO_AIRPORT, *BPN, *TRK, params, barge=True) == pytest.approx(53.66, abs=0.1)


def test_barge_sensitivity_changes_only_the_barge_leg() -> None:
    params = dataclasses.replace(load_inputs().parameters, barge_road_factor=1.0)

    # 516 km straight line from BPN to TRK at 0.08 USD per tonne-km.
    assert leg_cost(Leg.REFINERY_TO_AIRPORT, *BPN, *TRK, params, barge=True) == pytest.approx(41.28, abs=0.1)
    # PNK to PKN by road keeps the 1.3 factor: 494 km at 0.08.
    assert leg_cost(Leg.REFINERY_TO_AIRPORT, *PNK, *PKN, params) == pytest.approx(39.52, abs=0.1)


def test_only_a_refinery_to_airport_leg_can_be_a_barge() -> None:
    with pytest.raises(ValueError):
        leg_cost(Leg.DEPOT_TO_REFINERY, *BPN, *TRK, load_inputs().parameters, barge=True)
