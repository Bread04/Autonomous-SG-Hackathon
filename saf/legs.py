"""The three transport Legs of the supply chain."""

from enum import Enum


class Leg(Enum):
    BIOMASS_SITE_TO_DEPOT = "Farm to depot"
    DEPOT_TO_REFINERY = "Depot to refinery"
    REFINERY_TO_AIRPORT = "Refinery to airport"
