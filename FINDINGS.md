# Challenge 3: SAF Supply Chain in Kalimantan

## The problem

Design the cheapest yearly system for turning farm and forestry waste into Sustainable Aviation Fuel (SAF) and delivering it to Kalimantan's 4 airports.

```
80 biomass sites → Depots → Refineries → 4 airports
```

### Decisions to make

1. **Sites:** which of the 80 sites to use. They hold 6,800 kt in total and only 6,000 kt is needed.
2. **Facilities:** how many depots and refineries to build, and whether each is Small or Large.
3. **Locations:** coordinates for each facility, anywhere on land in Kalimantan.
4. **Flows:** how much moves from sites to depots, depots to refineries, and refineries to airports.

### Objective

Minimise annualised CapEx + fixed OpEx + variable OpEx + transport, while meeting every airport's demand.

### Deliverables

- Depot and refinery coordinates and sizes
- Material flow network
- Total yearly cost
- Truck trips for each leg (truck size affects trips only, not cost)

## Key numbers

| Item | Value |
|---|---|
| SAF demand | 300 kt per airport, 1,200 kt in total |
| Yield | 1 t biomass → 0.20 t SAF |
| Biomass needed | 6,000 kt per year |
| Depot mass loss | None |
| Capacity | Biomass intake, for depots and refineries |
| CapEx | Straight-line over 20 years, no interest |
| Fixed OpEx | 5% of CapEx per year |
| Distance | Great-circle distance × 1.3 |
| Tarakan (TRK) | Last leg by barge at 0.08 USD per tonne-km, no extra fixed cost |

Our own assumptions are allowed if stated and justified.

### Yearly cost per facility

| Facility | Size | Capacity (kt) | Annualised CapEx (USD) | Fixed OpEx (USD) | Total fixed per year (USD) | Variable (USD/t) |
|---|---|---:|---:|---:|---:|---:|
| Depot | Small | 150 | 112,500 | 112,500 | 225,000 | 5 |
| Depot | Large | 300 | 225,000 | 225,000 | 450,000 | 4 |
| Refinery | Small | 500 | 24.0M | 24.0M | 48.0M | 60 |
| Refinery | Large | 1,087 | 38.25M | 38.25M | 76.5M | 55 |

## Early findings

These come from the parameters alone. They ignore transport, so the optimiser may overturn them.

### Refineries

Six Large refineries is the cheapest mix that covers 6,000 kt before transport.

| Mix | Capacity (kt) | Fixed cost per year (USD) |
|---|---:|---:|
| 6 Large | 6,522 | 459.0M |
| 5 Large + 2 Small | 6,435 | 478.5M |
| 4 Large + 4 Small | 6,348 | 498.0M |
| 12 Small | 6,000 | 576.0M |

Large also costs less per tonne to run (55 vs 60 USD/t).

### Depots

- 20 Large depots cover exactly 6,000 kt at about 9M USD per year in fixed cost. 40 Small depots would cost 9M too, so the size choice depends on variable cost and transport.
- Large is cheaper per tonne to run (4 vs 5 USD/t), but 20 Large depots leave no spare capacity.

### Where the money goes

| Cost | Estimate per year (USD) |
|---|---:|
| Refineries (6 Large, fixed + 330M variable) | ~789M |
| Depots (20 Large, fixed + 24M variable) | ~33M |
| Transport | Not yet calculated |

### Where facilities should go

- **Refineries near the biomass, not the airports.** Moving 1 t of SAF costs 0.08 USD per km. Moving the 5 t of biomass behind it costs 0.60 USD per km on the depot-to-refinery leg, about 7.5 times more.
- **Depots close to refineries.** The depot-to-refinery leg (0.12 USD per tonne-km) costs more than the farm-to-depot leg (0.10), so the model has a reason to keep that second leg short.

### The core trade-off

Refineries are expensive, which favours a few large ones. The airports are far apart, which favours spreading them out. The optimiser has to balance the two.

## Judging criteria

Each project is scored by 3 judges. Each criterion gets 1 to 5, with these weights:

| Criterion | Weight | Key question | Strong | Weak |
|---|---:|---|---|---|
| Problem realism | 20% | Does this solve a specific aerospace workflow problem? | A credible user, narrow workflow and clear status quo | A generic aviation chatbot, or a solution looking for a problem |
| Technical soundness | 25% | Does the prototype work, with the right method for each task? | Working inputs and outputs, explicit constraints, and a sound LLM / non-LLM split | LLM-only legality checks, opaque risk scores, or a hard-coded demo |
| Honest evaluation | 20% | What was tested, against what baseline, and where does it fail? | A baseline, measured results, and a visible failure with a reason | Only success cases, unsupported accuracy claims, or hidden data limits |
| Trust and traceability | 20% | Can a qualified person verify the output before acting? | Checkable sources, visible uncertainty, and a clear refusal when needed | Confident unsourced answers, or a claim to replace expert judgement |
| Impact | 10% | What improves over the current process, and by how much? | A credible before/after measure and realistic adoption constraints | Large benefit claims with no baseline or unstated assumptions |
| Time discipline | 5% | Was the project submitted early and presented efficiently? | Earlier submission and a focused, complete presentation within 3 minutes | Later submission and a rushed, unfocused or over-time presentation |

### What judges look for

- **Problem realism:** name the user (for example a supply planner), the current process, and the cost in time, money or risk. Explain this challenge's constraints, not aviation in general.
- **Technical soundness:** show an end-to-end build that works beyond a scripted demo. Use LLMs for reading, retrieval, explanation and interaction. Use solvers, rules or statistics for optimisation, constraints and detection. An LLM doing arithmetic or scheduling scores as weak.
- **Honest evaluation:** state metrics, test data and results. Label synthetic data and its limits. Show one case where the system is wrong, uncertain or declines, explain why, and explain how the user knows.
- **Trust and traceability:** trace claims to a document, revision and section, a timestamped signal or an applied rule. Handle applicability and missing evidence. Keep the qualified person in control.
- **Impact:** compare against the stated baseline, and separate measured improvement from estimates.
- **Time discipline:** one combined score for submission time and a presentation within 3 minutes. Earlier submission does not substitute for quality or evidence.

### Scoring

- **Scale:** 1 = weak, 2 = limited, 3 = credible, 4 = strong, 5 = exceptional evidence.
- **Weighted total out of 100:** sum of (criterion score / 5 × criterion weight). For example, technical soundness scored 4/5 earns 20 of its 25 points.
- **Judges will ask:** "Where does this fail, and how would your user know?"
- **Judges reward** sound restraint, not presentation polish.

## Open items

- `Biomass location/kalimantan_80_locations_6800kt_full_range.csv` is not in this repo yet, and the model needs it.
- `challenge3_airports_4.csv` spells the Tarakan city as "Taraken". The IATA code and coordinates are what matter.
