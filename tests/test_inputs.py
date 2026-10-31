from collections.abc import Callable
from pathlib import Path

import pandas as pd
import pytest

from saf.inputs import BIOMASS_CSV, InputError, load_inputs

# District totals (kt) from Project Summary.pdf, section 2.3.
PDF_DISTRICT_KT = {
    "Ketapang": 1811.8,
    "Sanggau": 1142.9,
    "Kutai Kartanegara": 985.7,
    "Kotawaringin Timur": 946.6,
    "Kotawaringin Barat": 893.2,
    "Paser": 556.2,
    "Tanah Laut": 274.7,
    "Bulungan": 189.0,
}


def test_biomass_sites_match_the_project_summary() -> None:
    sites = load_inputs().biomass_sites

    assert len(sites) == 80
    assert sites["supply_kt"].sum() == pytest.approx(6800.0)
    district_kt = sites.groupby("district")["supply_kt"].sum().to_dict()
    assert district_kt == pytest.approx(PDF_DISTRICT_KT, abs=0.1)


def _drop_last_row(df: pd.DataFrame) -> pd.DataFrame:
    return df.iloc[:-1]


def _drop_supply_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns="production_kilotons")


def _duplicate_an_id(df: pd.DataFrame) -> pd.DataFrame:
    first, second = df["location_id"].iloc[0], df["location_id"].iloc[1]
    return df.assign(location_id=df["location_id"].replace({second: first}))


def _blank_a_latitude(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(latitude=df["latitude"].mask(df.index == 0))


def _inflate_one_biomass_site(df: pd.DataFrame) -> pd.DataFrame:
    first = df.index == 0
    return df.assign(
        production_kilotons=df["production_kilotons"].mask(first, df["production_kilotons"] + 10),
        production_tonnes=df["production_tonnes"].mask(first, df["production_tonnes"] + 10_000),
    )


def _tonnes_disagree_with_kt(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(production_tonnes=df["production_tonnes"].mask(df.index == 0, df["production_tonnes"] + 1))


@pytest.mark.parametrize(
    "corrupt",
    [
        _drop_last_row,
        _drop_supply_column,
        _duplicate_an_id,
        _blank_a_latitude,
        _inflate_one_biomass_site,
        _tonnes_disagree_with_kt,
    ],
)
def test_broken_biomass_data_stops_the_run(
    raw_copy: Path, corrupt: Callable[[pd.DataFrame], pd.DataFrame]
) -> None:
    path = raw_copy / BIOMASS_CSV
    corrupt(pd.read_csv(path)).to_csv(path, index=False)

    with pytest.raises(InputError):
        load_inputs(raw_copy)
