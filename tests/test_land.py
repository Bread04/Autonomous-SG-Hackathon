import pytest

from saf.land import is_on_kalimantan_mainland


@pytest.mark.parametrize(
    ("place", "lat", "lon"),
    [
        ("Pontianak airport", -0.1507, 109.404),
        ("Pangkalan Bun airport", -2.7052, 111.673),
        ("Banjarmasin", -3.32, 114.59),
        ("Samarinda", -0.50, 117.15),
    ],
)
def test_mainland_kalimantan_passes(place: str, lat: float, lon: float) -> None:
    assert is_on_kalimantan_mainland(lat, lon), place


@pytest.mark.parametrize(
    ("place", "lat", "lon"),
    [
        ("Kuching, Sarawak", 1.55, 110.35),
        ("Bandar Seri Begawan, Brunei", 4.89, 114.94),
        ("Kota Kinabalu, Sabah", 5.98, 116.07),
        ("Tarakan airport, island", 3.3267, 117.5694),
        ("Laut Island", -3.60, 116.20),
        ("Java Sea", -4.50, 112.00),
    ],
)
def test_everywhere_else_fails(place: str, lat: float, lon: float) -> None:
    assert not is_on_kalimantan_mainland(lat, lon), place


def test_checks_many_points_at_once() -> None:
    result = is_on_kalimantan_mainland([-0.1507, 1.55], [109.404, 110.35])

    assert result.tolist() == [True, False]
