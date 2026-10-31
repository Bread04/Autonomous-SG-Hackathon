# Kalimantan SAF Supply Chain

The yearly system that turns farm and forestry waste into Sustainable Aviation Fuel and delivers it to Kalimantan's four airports.

## Language

### Network

**Biomass Site**:
One of the 80 given supply points, each with a fixed yearly tonnage and coordinates.
_Avoid_: Farm, site, location

**Flagged Biomass Site**:
A Biomass Site whose given coordinates fall outside the Kalimantan Mainland, kept as usable supply but reported as a data limit.
_Avoid_: Offshore site, invalid site

**Kalimantan Mainland**:
The Indonesian part of Borneo's main landmass, excluding Sarawak, Sabah, Brunei, Tarakan and smaller islands.
_Avoid_: Borneo, Kalimantan land

**Candidate Location**:
A position on the Kalimantan Mainland where a Facility might be built.
_Avoid_: Site, candidate site, facility site

**Facility**:
A Depot or Refinery that the plan builds.
_Avoid_: Plant, unit, site

**Depot**:
A Facility that pre-processes biomass with no mass loss.
_Avoid_: Pre-processing site, hub

**Refinery**:
A Facility that converts biomass to SAF.
_Avoid_: Plant

**Airport**:
One of PNK, PKN, BPN or TRK, each with a fixed yearly SAF demand.
_Avoid_: Destination

### Transport

**Leg**:
One of the three transport hops: Biomass Site to Depot, Depot to Refinery, Refinery to Airport.
_Avoid_: Stage, echelon, route

**Barge Leg**:
A Refinery to Airport Leg ending at TRK, which trucks cannot reach.
_Avoid_: Ferry, sea crossing
