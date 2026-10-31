"""Load and validate the challenge inputs from data/raw."""

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from saf.land import km_from_mainland
from saf.legs import Leg

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
BIOMASS_CSV = "kalimantan_80_locations_6800kt_full_range.csv"
WORKBOOK = "challenge3_parameters.xlsx"
AIRPORTS_CSV = "challenge3_airports_4.csv"
AIRPORT_CODES = {"PNK", "PKN", "BPN", "TRK"}
COORDINATE_TOLERANCE_DEG = 1e-6

BIOMASS_SITE_COUNT = 80
BIOMASS_TOTAL_KT = 6800.0
BIOMASS_TOLERANCE_KT = 1e-6
BIOMASS_COLUMNS = [
    "location_id",
    "province",
    "district",
    "production_kilotons",
    "production_tonnes",
    "latitude",
    "longitude",
]


class InputError(ValueError):
    """An input file is broken, so no result built on it can be trusted."""


@dataclass(frozen=True)
class Parameters:
    facilities: pd.DataFrame
    """Indexed by (facility, size): capacity_kt of biomass intake, fixed_usd_per_year, variable_usd_per_t."""
    leg_rate_usd_per_tkm: dict[Leg, float]
    truck_payload_t: pd.DataFrame
    """Indexed by Leg: small and large truck payloads in tonnes."""
    saf_yield: float
    """Tonnes of SAF per tonne of biomass."""
    road_factor: float
    barge_road_factor: float
    """Road factor on the Barge Leg to TRK. The workbook gives one factor for all Legs; replace it for sensitivity."""


@dataclass(frozen=True)
class Inputs:
    biomass_sites: pd.DataFrame
    """One row per Biomass Site. Flagged Biomass Sites lie off the Kalimantan Mainland but stay usable supply."""
    airports: pd.DataFrame
    parameters: Parameters

    @property
    def biomass_required_kt(self) -> float:
        """Biomass needed to meet every Airport's demand."""
        return float(self.airports["demand_kt"].sum()) / self.parameters.saf_yield

    @property
    def min_flagged_supply_kt(self) -> float:
        """Biomass that must come from Flagged Biomass Sites, even if every other Biomass Site is used in full."""
        unflagged_kt = float(self.biomass_sites.loc[~self.biomass_sites["flagged"], "supply_kt"].sum())
        return max(0.0, self.biomass_required_kt - unflagged_kt)


def load_inputs(raw_dir: Path = RAW_DIR) -> Inputs:
    try:
        return Inputs(
            biomass_sites=_load_biomass_sites(raw_dir / BIOMASS_CSV),
            airports=_load_airports(raw_dir / WORKBOOK, raw_dir / AIRPORTS_CSV),
            parameters=_load_parameters(raw_dir / WORKBOOK),
        )
    except KeyError as missing:
        raise InputError(f"an input file is missing column or row {missing}") from missing


def _load_biomass_sites(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)

    missing = set(BIOMASS_COLUMNS) - set(raw.columns)
    _require(not missing, f"{path.name} is missing columns {sorted(missing)}")
    _require(not raw[BIOMASS_COLUMNS].isna().any().any(), f"{path.name} has blank values")
    _require(len(raw) == BIOMASS_SITE_COUNT, f"{path.name} has {len(raw)} rows, expected {BIOMASS_SITE_COUNT}")
    _require(raw["location_id"].is_unique, f"{path.name} has duplicate location_id values")
    total_kt = raw["production_kilotons"].sum()
    _require(abs(total_kt - BIOMASS_TOTAL_KT) < BIOMASS_TOLERANCE_KT, f"{path.name} totals {total_kt} kt, expected {BIOMASS_TOTAL_KT}")
    tonnes_mismatch = (raw["production_tonnes"] - raw["production_kilotons"] * 1000).abs() > BIOMASS_TOLERANCE_KT * 1000
    _require(not tonnes_mismatch.any(), f"{path.name} has production_tonnes != kt x 1000")

    sites = raw.rename(
        columns={
            "location_id": "biomass_site_id",
            "production_kilotons": "supply_kt",
            "latitude": "lat",
            "longitude": "lon",
        }
    )
    sites = sites[["biomass_site_id", "province", "district", "supply_kt", "lat", "lon"]]
    km = [km_from_mainland(lat, lon) for lat, lon in zip(sites["lat"], sites["lon"])]
    return sites.assign(km_from_mainland=km, flagged=[k > 0 for k in km])


def _load_airports(workbook: Path, csv: Path) -> pd.DataFrame:
    """Airports from the workbook, which must agree with the airport CSV."""
    airports = _read_sheet(workbook, "airports", first_column="iata").set_index("iata").sort_index()
    check = pd.read_csv(csv).set_index("iata").sort_index()

    _require(set(airports.index) == AIRPORT_CODES, f"{workbook.name} airports are {sorted(airports.index)}")
    _require(list(check.index) == list(airports.index), f"{csv.name} airports differ from {workbook.name}")
    _require(
        bool((check["saf_demand_kt_per_year"] == airports["saf_demand_kt_per_year"]).all()),
        f"{csv.name} SAF demand differs from {workbook.name}",
    )
    for column in ("latitude", "longitude"):
        drift = (check[column] - airports[column].astype(float)).abs()
        _require(bool((drift <= COORDINATE_TOLERANCE_DEG).all()), f"{csv.name} {column} differs from {workbook.name}")

    return pd.DataFrame(
        {
            "iata": airports.index,
            "lat": airports["latitude"].astype(float).to_numpy(),
            "lon": airports["longitude"].astype(float).to_numpy(),
            "demand_kt": airports["saf_demand_kt_per_year"].astype(float).to_numpy(),
        }
    )


def _load_parameters(path: Path) -> Parameters:
    assumptions = _read_sheet(path, "assumptions", first_column="parameter").set_index("parameter")["value"].astype(str)
    capex_life_years = float(_parse(assumptions, "CapEx", r"over (\d+) years"))
    _require(assumptions["Depot mass loss"].startswith("0%"), "the model assumes depots lose no mass")

    facilities = _read_sheet(path, "facilities", first_column="facility").set_index(["facility", "size"])
    annualised = facilities["capex_usd"] / capex_life_years
    _require(
        bool(((facilities["annualised_capex_usd_per_year"] - annualised).abs() < 1).all()),
        f"{path.name} annualised CapEx is not CapEx / {capex_life_years:g} years",
    )
    facilities = pd.DataFrame(
        {
            "capacity_kt": facilities["capacity_kt_biomass_in_per_year"],
            "fixed_usd_per_year": annualised + facilities["fixed_opex_usd_per_year"],
            "variable_usd_per_t": facilities["variable_opex_usd_per_tonne_in"],
        }
    )

    transport = _read_sheet(path, "transport", first_column="leg")
    legs = {leg.value: leg for leg in Leg}
    _require(set(transport["leg"]) == set(legs), f"{path.name} transport legs are {sorted(transport['leg'])}")
    rates = {legs[name]: float(rate) for name, rate in zip(transport["leg"], transport["cost_usd_per_tonne_km"])}
    transport = transport.set_index(transport["leg"].map(legs))

    road_factor = float(_parse(assumptions, "Distance", r"x ([\d.]+) road factor"))
    return Parameters(
        facilities=facilities,
        leg_rate_usd_per_tkm=rates,
        truck_payload_t=transport[["small_truck_t", "large_truck_t"]],
        saf_yield=float(_parse(assumptions, "Refinery yield", r"([\d.]+) t SAF per t biomass")),
        road_factor=road_factor,
        barge_road_factor=road_factor,
    )


def _read_sheet(path: Path, sheet: str, *, first_column: str) -> pd.DataFrame:
    """Read a sheet whose header row sits below a free-text note and blank rows."""
    cells = pd.read_excel(path, sheet_name=sheet, header=None)
    header_rows = cells.index[cells[0] == first_column]
    _require(len(header_rows) == 1, f"{path.name} sheet {sheet!r} has no single {first_column!r} header row")
    header = header_rows[0]
    table = cells.iloc[header + 1 :].dropna(how="all")
    table.columns = pd.Index(cells.iloc[header])
    return table.reset_index(drop=True).infer_objects()


def _parse(assumptions: "pd.Series[str]", name: str, pattern: str) -> str:
    match = re.search(pattern, assumptions.get(name, ""))
    _require(match is not None, f"cannot read {name!r} from the assumptions sheet")
    assert match is not None
    return match.group(1)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InputError(message)
