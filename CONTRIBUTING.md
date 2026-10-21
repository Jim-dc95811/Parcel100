# Contributing

Parcel100 is intentionally small and deterministic. Contributions should preserve the core operating contract unless a change is explicitly discussed first.

## Core compatibility contract

A normal build must continue to behave as:

```text
one whole-degree Master 4 input
-> established 01-100 Master 4 cell addresses
-> deterministic output filenames
-> skip completed existing filenames on resumed runs
-> public ArcGIS FeatureServer polygon queries
-> selected fields only
-> ID discovery before heavy feature retrieval
-> retry transient service failures
-> four-part fallback for repeatedly failing transient full-cell ID queries
-> EPSG:4326 GeoJSON
-> populated cells written
-> empty cells skipped
```

Do not casually change cell numbering, output filenames, coordinate ordering, resume semantics or default Florida behavior. Those details are part of the field workflow and companion Master 4 system.

## Useful contributions

Good candidates include:

- support for additional public FeatureServer quirks;
- clearer service/field discovery;
- improved error reporting;
- regression tests for geometry conversion;
- optional integrity validation for existing resume files;
- measured hardening for services that fail at their advertised feature-batch size;
- documentation for parcel services in additional states/counties;
- measured viewer-performance results with real GeoJSON cells.

## Before proposing a behavioral change

Document:

1. the problem being solved;
2. the existing behavior;
3. the exact proposed change;
4. compatibility impact on existing filenames/cell numbering/resume/output;
5. how the change was tested.

## Testing expectations

At minimum, changes affecting production should verify:

- GUI starts successfully and reports the intended version;
- service metadata can be read;
- selected fields are preserved;
- the Florida Recommended set still selects `Acres` when available;
- existing completed filenames are skipped on a resumed run;
- empty cells are skipped rather than misclassified errors;
- transient retry/fallback behavior does not convert hard failures into false empty cells;
- populated cells create valid GeoJSON;
- output coordinates are WGS 84 / EPSG:4326;
- polygon and multipolygon geometry still opens correctly in a real GIS/viewer;
- Master 4 cell numbering and filenames remain unchanged unless intentionally versioned.

## Data and privacy

Do not commit downloaded parcel datasets, bulk owner records, API tokens or other credential/private data to this repository.

Screenshots used for documentation should be limited to legitimate public-data examples and should not expose credentials, tokens or non-public information.
