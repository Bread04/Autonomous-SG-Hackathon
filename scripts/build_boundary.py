"""Cut the Kalimantan Mainland out of Natural Earth 10m admin-1 provinces.

Usage: python scripts/build_boundary.py <ne_10m_admin_1_states_provinces.geojson>
"""

import json
import sys
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

OUTPUT = Path(__file__).parent.parent / "data" / "boundary" / "kalimantan_mainland.geojson"
PROVINCES = {"ID-KB", "ID-KI", "ID-KS", "ID-KT"}


def main(source: Path) -> None:
    features = json.loads(source.read_text(encoding="utf-8"))["features"]
    provinces = [
        shape(f["geometry"]).buffer(0)
        for f in features
        if f["properties"].get("iso_3166_2") in PROVINCES
    ]
    if len(provinces) != len(PROVINCES):
        raise SystemExit(f"expected {len(PROVINCES)} provinces, found {len(provinces)}")

    mainland = max(unary_union(provinces).geoms, key=lambda part: part.area)
    OUTPUT.write_text(json.dumps(mapping(mainland)), encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
