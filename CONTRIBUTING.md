# Contributing

Parcel100 is intentionally small and deterministic. Contributions should preserve the core operating contract unless a change is explicitly discussed first.

## Core compatibility contract

A normal build must continue to behave as:

```text
one whole-degree Master 4 input
-> established 01-100 Master 4 cell addresses
-> public ArcGIS FeatureServer polygon queries
-> selected fields only
-> EPSG:4326 GeoJSON
-> populated cells written
-> empty cells skipped
```

Do not casually change cell numbering, output filenames, coordinate ordering or default Florida behavior. Those details are part of the field workflow and companion Master 4 system.

## Useful contributions

Good candidates include:

- support for additional public FeatureServer quirks;
- clearer service/field discovery;
- improved error reporting;
- regression tests for geometry conversion;
- documentation for parcel services in additional states/counties;
- measured viewer-performance results with real GeoJSON cells.

## Before proposing a behavioral change

Document:

1. the problem being solved;
2. the existing behavior;
3. the exact proposed change;
4. compatibility impact on existing filenames/cell numbering/output;
5. how the change was tested.

## Testing expectations

At minimum, changes affecting production should verify:

- GUI starts successfully;
- service metadata can be read;
- selected fields are preserved;
- empty cells are skipped rather than misclassified errors;
- populated cells create valid GeoJSON;
- output coordinates are WGS 84 / EPSG:4326;
- polygon and multipolygon geometry still opens correctly in a real GIS/viewer;
- Master 4 cell numbering and filenames remain unchanged unless intentionally versioned.

## Data and privacy

Do not commit downloaded parcel datasets, owner records, addresses, API tokens or other personal/credential data to this repository.

Use synthetic or non-sensitive examples when adding tests or screenshots.
