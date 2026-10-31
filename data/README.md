# Data

## raw/

The challenge inputs, read-only. `saf.inputs.load_inputs()` reads them and stops on anything broken.

| File | Used for |
|---|---|
| `challenge3_parameters.xlsx` | Every parameter, and the Airports. Overrides `Project Summary.pdf` wherever they differ. |
| `challenge3_airports_4.csv` | Cross-check only: must match the workbook's Airports (codes and demand exactly, coordinates within 1e-6 degrees). |
| `kalimantan_80_locations_6800kt_full_range.csv` | The 80 Biomass Sites. |
| `airports.dat` | Reference only, not loaded. OpenFlights source of the Airport coordinates; agrees with the CSV on all four. |

## boundary/

`kalimantan_mainland.geojson` is the Kalimantan Mainland: the largest landmass in the union of the four Kalimantan provinces (ID-KB, ID-KI, ID-KS, ID-KT). Natural Earth predates North Kalimantan, so it sits inside ID-KI.

- **Source:** Natural Earth 10m `ne_10m_admin_1_states_provinces.geojson`, public domain, from https://github.com/nvkelso/natural-earth-vector (master at `ca96624`, VERSION `5.2.0-pre`).
- **Rebuild:** `python scripts/build_boundary.py <path to that geojson>`
- **Limit:** the 10m coastline is coarse. Points within about a kilometre of the coast can be misjudged; Balikpapan airport, on land, falls just outside.
