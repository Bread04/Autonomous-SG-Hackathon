from pathlib import Path

import openpyxl
import pytest

from saf.inputs import WORKBOOK, InputError, load_inputs
from saf.legs import Leg


def test_parameters_match_the_brief() -> None:
    params = load_inputs().parameters

    assert params.saf_yield == pytest.approx(0.20)
    assert params.road_factor == pytest.approx(1.3)
    assert params.leg_rate_usd_per_tkm == pytest.approx(
        {Leg.BIOMASS_SITE_TO_DEPOT: 0.10, Leg.DEPOT_TO_REFINERY: 0.12, Leg.REFINERY_TO_AIRPORT: 0.08}
    )


@pytest.mark.parametrize(
    ("facility", "size", "capacity_kt", "fixed_usd_per_year", "variable_usd_per_t"),
    [
        # "Yearly cost per facility" table in FINDINGS.md.
        ("Depot", "Small", 150, 225_000, 5),
        ("Depot", "Large", 300, 450_000, 4),
        ("Refinery", "Small", 500, 48_000_000, 60),
        ("Refinery", "Large", 1087, 76_500_000, 55),
    ],
)
def test_facility_costs_match_the_brief(
    facility: str, size: str, capacity_kt: float, fixed_usd_per_year: float, variable_usd_per_t: float
) -> None:
    row = load_inputs().parameters.facilities.to_dict("index")[(facility, size)]

    assert row["capacity_kt"] == capacity_kt
    assert row["fixed_usd_per_year"] == pytest.approx(fixed_usd_per_year)
    assert row["variable_usd_per_t"] == variable_usd_per_t


def test_a_missing_workbook_column_stops_the_run(raw_copy: Path) -> None:
    path = raw_copy / WORKBOOK
    workbook = openpyxl.load_workbook(path)
    workbook["transport"].delete_cols(3)  # cost_usd_per_tonne_km
    workbook.save(path)

    with pytest.raises(InputError):
        load_inputs(raw_copy)
