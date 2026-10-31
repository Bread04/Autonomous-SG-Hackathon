from collections.abc import Callable
from pathlib import Path

import pandas as pd
import pytest

from saf.inputs import AIRPORTS_CSV, InputError, load_inputs


def test_four_airports_each_need_300_kt_of_saf() -> None:
    inputs = load_inputs()

    assert inputs.airports.set_index("iata")["demand_kt"].to_dict() == {
        "PNK": 300,
        "PKN": 300,
        "BPN": 300,
        "TRK": 300,
    }
    # The brief: 1,200 kt of SAF at 20% yield needs 6,000 kt of biomass.
    assert inputs.biomass_required_kt == pytest.approx(6000.0)


def _change_demand(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(saf_demand_kt_per_year=df["saf_demand_kt_per_year"].mask(df.index == 0, 310))


def _move_an_airport(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(latitude=df["latitude"].mask(df.index == 0, df["latitude"] + 1e-4))


def _rename_an_airport(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(iata=df["iata"].replace({"TRK": "TRX"}))


def _drop_demand_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns="saf_demand_kt_per_year")


@pytest.mark.parametrize("corrupt", [_change_demand, _move_an_airport, _rename_an_airport, _drop_demand_column])
def test_workbook_and_airport_csv_must_agree(
    raw_copy: Path, corrupt: Callable[[pd.DataFrame], pd.DataFrame]
) -> None:
    path = raw_copy / AIRPORTS_CSV
    corrupt(pd.read_csv(path)).to_csv(path, index=False)

    with pytest.raises(InputError):
        load_inputs(raw_copy)


def test_coordinate_rounding_between_the_two_sources_is_tolerated(raw_copy: Path) -> None:
    path = raw_copy / AIRPORTS_CSV
    df = pd.read_csv(path)
    df.assign(latitude=df["latitude"] + 1e-9).to_csv(path, index=False)

    assert len(load_inputs(raw_copy).airports) == 4
