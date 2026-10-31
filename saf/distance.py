"""Distances and per-tonne transport costs between any two points."""

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import ArrayLike, NDArray

from saf.legs import Leg

if TYPE_CHECKING:
    from saf.inputs import Parameters

EARTH_RADIUS_KM = 6371.0


def dist(
    lat1: ArrayLike, lon1: ArrayLike, lat2: ArrayLike, lon2: ArrayLike, *, road_factor: float
) -> NDArray[np.float64]:
    """Great-circle distance in km times the road factor. Broadcasts over arrays."""
    phi1, lam1, phi2, lam2 = (np.radians(np.asarray(v, dtype=float)) for v in (lat1, lon1, lat2, lon2))
    h = np.sin((phi2 - phi1) / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin((lam2 - lam1) / 2) ** 2
    return np.asarray(2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(h)) * road_factor, dtype=np.float64)


def leg_cost(
    leg: Leg,
    lat1: ArrayLike,
    lon1: ArrayLike,
    lat2: ArrayLike,
    lon2: ArrayLike,
    params: "Parameters",
    *,
    barge: bool = False,
) -> NDArray[np.float64]:
    """Transport cost in USD per tonne moved along a Leg. Broadcasts over arrays.

    A Barge Leg (Refinery to TRK) uses the Refinery to Airport rate and its own barge road factor.
    """
    if barge and leg is not Leg.REFINERY_TO_AIRPORT:
        raise ValueError(f"only a Refinery to Airport Leg can be a Barge Leg, not {leg.name}")
    road_factor = params.barge_road_factor if barge else params.road_factor
    km = dist(lat1, lon1, lat2, lon2, road_factor=road_factor)
    return np.asarray(params.leg_rate_usd_per_tkm[leg] * km, dtype=np.float64)
