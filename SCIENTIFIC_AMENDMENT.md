# Prospective scientific amendment — 9 November 2026

This amendment supersedes the infeasible significance rule in the historical 30 October plan. The original sealed document is retained. No real-city calibration, optimisation or confirmatory result has been observed. G0 uses synthetic geometry and is an engineering check only.

## Corrected statistical scope

The historical H3 hypothesis proposed at least 15% relative exposure reduction against a preselected search control, with the same budget of 2,000 equivalent forward evaluations per shade design. Its planned factorial comparison had four variants:

| Planned shadow operator | Gradient search | Grid or random search |
|---|---|---|
| New differentiable operator using the geometric-computation pattern explored in Neuro3D | A | B |
| Independently implemented differentiable shadow map, with matched resolution and calibration budget | C | D |

A versus C was intended to isolate the operator while holding the optimiser fixed. Final designs from every variant would be scored with the same Radiance reference. These comparative variants remain future work; the G0 code in this repository is their synthetic engineering precursor.

The historical plan reduced its nine district-by-seed outcomes to three district medians, then required a two-sided exact Wilcoxon p < 0.05. Enumerating the eight possible signs gives a minimum p of 2/8 = 0.25. This criterion cannot be reached, even with three improvements in the same direction.

The three proposed pilot districts therefore support descriptive and exploratory comparisons only. Seeds, stops, hours and months within one district do not become independent geographic replication. Neither H3 nor the A-versus-C attribution claim may be labelled confirmed or disproved by that three-district significance test.

A confirmatory design will be sealed after the licensed data inventory establishes feasible, genuinely independent geographic units and before any calibration or comparative optimisation. It must specify its sample manifest, primary metric, aggregation, missing-data policy, multiplicity correction and detectable effect assumptions. A small sample remains exploratory; units must not be added or removed in response to favourable results.

`statistical_design.py` supplies an executable planning alternative, rather than an unearned claim of sufficient power: two predeclared directional sign tests at alpha 0.025 each would control two primary comparisons by Bonferroni. For 20 independent units, at least 15 positive signs are needed. Under the explicit assumption that a unit has an 0.8 probability of a positive sign, power is 0.8042. Twelve units yield only 0.5583. These are conditional sign-test calculations, not measured effects or Wilcoxon power. No twenty-unit sample has been enrolled or declared independent.

If this alternative is adopted, one primary contrast would use the per-unit improvement relative to the 15% target, and the other would use A versus C at zero improvement. Ties would count as failures for a conservative directional test. The final protocol must specify the exposure aggregation and handling of zero baselines first. Until then there is no confirmatory H3 success criterion in force.

## Corrected model meanings

- Waiting and walking are different time quantities. Under uniform passenger arrival on a periodic usable-service schedule, expected wait is sum(h²)/(2 sum(h)), in minutes. The mean headway divided by two is wrong for unequal headways. A [10,30]-minute schedule gives 12.5 minutes, rather than 10. Real arrival patterns, cancellations and service compatibility require separate evidence.
- Walking exposure uses time along a route, not bus waiting time. Pooling departures for unrelated destinations would underestimate usable-service wait and is excluded.
- The new horizontal-rectangle operator and its smooth edge are engineering components written for this project. No existing Neuro3D solar operator, physical penumbra, irradiance accuracy or superiority is claimed. Diffuse irradiance, solar-disk integration, real terrain and professional Radiance comparisons remain future work.
- The historical assertions that nobody has combined these sources and that this would be the first such map are unverified. They are excluded from public claims pending a literature and product search.
- H1's future Radiance comparison must remain separate from G0's synthetic ray/triangle consistency check. Passing G0 cannot be reported as H1 passing.
- The historical H4 meteorological association is a seasonal/climate consistency check. It cannot establish stop-level exposure accuracy or a health benefit.

## Current preregistered engineering work

`preregister.json` fixes synthetic seed, sample counts, tolerances and negative controls before execution. The independent CPU reference uses ray/triangle intersection; the candidate projects ground-to-sun rays into a rotated rectangle. Autograd is compared with central finite differences. Smooth-edge checks are restricted to a stated distance from boundaries; invalid inputs and boundary conventions have separate controls. Runtime samples are recorded without a speedup threshold.

Dataset acquisition, source attribution and per-operator licences are the next gate before real-city work. The public app and final Japanese work submission remain unfinished.
