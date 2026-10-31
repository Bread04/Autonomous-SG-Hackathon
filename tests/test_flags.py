from saf.inputs import load_inputs

# Biomass Sites more than 2 km from any land in Natural Earth 10m land, islands included, measured
# separately from this code before the build. Distance to the mainland can only be equal or larger.
KM_FROM_ANY_LAND = {
    "KAL_SUP_80": 37.5,
    "KAL_SUP_31": 32.0,
    "KAL_SUP_22": 27.6,
    "KAL_SUP_62": 25.3,
    "KAL_SUP_50": 20.3,
    "KAL_SUP_43": 19.7,
    "KAL_SUP_03": 18.1,
    "KAL_SUP_32": 17.6,
    "KAL_SUP_37": 16.6,
    "KAL_SUP_69": 11.4,
    "KAL_SUP_58": 4.6,
    "KAL_SUP_51": 2.3,
}


def test_biomass_sites_off_the_mainland_are_flagged_with_their_distance() -> None:
    sites = load_inputs().biomass_sites.set_index("biomass_site_id")

    flagged = sites[sites["flagged"]]
    km_from_mainland = flagged["km_from_mainland"].to_dict()
    assert set(KM_FROM_ANY_LAND) <= set(km_from_mainland)
    for biomass_site_id, km in KM_FROM_ANY_LAND.items():
        # 0.5 km allows for the two Natural Earth files drawing the coast slightly differently.
        assert km_from_mainland[biomass_site_id] >= km - 0.5, biomass_site_id


def test_flagged_biomass_sites_stay_usable_supply() -> None:
    sites = load_inputs().biomass_sites

    assert len(sites) == 80
    assert (sites.loc[~sites["flagged"], "km_from_mainland"] == 0).all()


def test_plan_must_draw_on_flagged_biomass_sites() -> None:
    # Unflagged supply is at most 6,800 - 1,058.7 = 5,741.3 kt against 6,000 kt needed.
    assert load_inputs().min_flagged_supply_kt >= 258.7
