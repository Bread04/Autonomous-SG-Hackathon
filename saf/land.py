"""Whether points lie on the Kalimantan Mainland.

The boundary comes from Natural Earth 10m admin-1 provinces (see data/README.md), so coastal
points can be misjudged by around a kilometre.
"""

import json
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
import shapely
from numpy.typing import ArrayLike, NDArray
from shapely.geometry import Point, shape
from shapely.ops import nearest_points

from saf.distance import dist

BOUNDARY = Path(__file__).parent.parent / "data" / "boundary" / "kalimantan_mainland.geojson"


@cache
def _mainland() -> Any:
    polygon = shape(json.loads(BOUNDARY.read_text(encoding="utf-8")))
    shapely.prepare(polygon)
    return polygon


def is_on_kalimantan_mainland(lat: ArrayLike, lon: ArrayLike) -> NDArray[np.bool_]:
    """True where a point is on the Kalimantan Mainland. Broadcasts over arrays."""
    return np.asarray(shapely.contains_xy(_mainland(), np.asarray(lon, dtype=float), np.asarray(lat, dtype=float)))


def km_from_mainland(lat: float, lon: float) -> float:
    """Great-circle km from a point to the nearest edge of the Kalimantan Mainland; 0 when on it."""
    point = Point(lon, lat)
    if _mainland().contains(point):
        return 0.0
    nearest = nearest_points(_mainland(), point)[0]
    return float(dist(lat, lon, nearest.y, nearest.x, road_factor=1.0))
