# Independent H0 review — 14 November 2026

Clean-context, read-only verification by a separate cog-verifier, using its own Python controls. No material issue was found within scope. All 268,154 CSV objects have unique IDs and valid extents inside declared file envelopes. ZIP metadata:408 building GML members,3,409,388,878 uncompressed bytes. Two source GML files (315 buildings including LOD2) were sampled with ElementTree: no bbox differences or parts. EPSG6697 axes checked from the EPSG database through pyproj. Both source hashes recomputed; GTFS CRC, relationships, chronology and the511-trip/658-stop schedule scenario checked independently.

This is a data-consistency review and limited XML sample, not independent physical validation. It does not establish topological validity, ground-truth accuracy, current operation, H1/H3/H4, a complete application or an official final submission.

The ten full deterministic author checks are in results/H0_CHECKS.json. Later portable-path changes are disclosed in PORTABILITY_DELTA.json and tested separately with real GTFS plus an explicitly synthetic two-building fixture; see PORTABILITY_CHECKS.json. No additional real-city effect or GPU experiment is implied.
