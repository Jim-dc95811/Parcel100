# Parcel100 Technical Notes

## Version

Current public source: **Parcel100 1.4**.

## Design goal

Parcel100 converts one Master 4 1-degree box into up to 100 geographically indexed parcel GeoJSON files without requiring QGIS in the production path.

The production chain is:

```text
Master 4 input
    -> 100 geographic cells
    -> resume-skip existing outputs
    -> FeatureServer object-ID query per unfinished cell
    -> retry transient failures
    -> if needed, four-part ID fallback
    -> skip empty cells
    -> batched feature queries for populated cells
    -> Esri polygon rings -> GeoJSON Polygon/MultiPolygon
    -> EPSG:4326 GeoJSON files
```

## Dependencies

Python standard library only:

- `json`
- `math`
- `re`
- `threading`
- `time`
- `urllib`
- `pathlib`
- `tkinter`

No `requests`, GDAL, Fiona, GeoPandas, Shapely, ArcPy, or QGIS Python environment is required.

## Master 4 input

The parser requires exactly four whole-degree edges in this order:

```text
west,east,south,north
```

Example:

```text
82w,81w,30n,31n
```

The longitude span and latitude span must each be exactly 1 degree.

## Cell addressing

Parcel100 intentionally matches the established Master4 Grid Maker 01-100 addressing logic.

The 1-degree box is divided into 10 rows and 10 columns. The implementation is hemisphere-aware and uses absolute decimal-degree position so the same cell-number concept works east/west and north/south of the equator.

Output uses three digits:

```text
001
002
...
100
```

Example filename:

```text
W082W081N031N030-055-Parcels.geojson
```

## Service discovery

The GUI accepts a direct ArcGIS FeatureServer **layer** URL.

Parcel100 requests:

```text
f=json
```

from the layer endpoint and verifies:

- a field schema is present;
- geometry type is `esriGeometryPolygon`.

The field list shown in the GUI comes from the service metadata, including field aliases when available.

The Florida field suggestions are only preferences for the known statewide layer. Other services are discovered dynamically.

## Resume / existing-file behavior

Before making any server request for a cell, Parcel100 computes the exact expected output filename. If that path already exists, the cell is counted as an existing file and skipped.

This creates simple durable resume behavior for interrupted builds: rerun the same Master 4 against the same output folder and completed cell files are not redownloaded.

Current caution: the program trusts an existing expected filename as complete. It does not validate JSON integrity or a checksum before skipping.

## Empty-cell probe

Each unfinished cell is first queried with:

```text
where=1=1
geometry=<west,south,east,north>
geometryType=esriGeometryEnvelope
inSR=4326
spatialRel=esriSpatialRelIntersects
returnIdsOnly=true
returnGeometry=false
```

If the service successfully returns no object IDs, the cell is marked empty and no GeoJSON file is written.

A service/network failure is not treated as empty.

This distinction matters for Master 4 boxes that include ocean, another state, or any area outside the selected parcel service's coverage.

## Retry behavior

Network/service requests use:

```text
TIMEOUT = 90 seconds
RETRIES = 3
```

Between failed attempts Parcel100 waits progressively longer: 1.5 seconds and then 3.0 seconds.

Retry status is surfaced in the GUI during build operations so a slow or unstable service does not simply look frozen.

ArcGIS JSON responses containing an `error` object are surfaced as failures rather than silently accepted.

## Difficult-cell four-part fallback

A full-cell object-ID query can fail repeatedly even when smaller queries against the same service succeed.

Parcel100 1.3/1.4 classifies known transient failure patterns such as:

```text
502
503
504
Gateway Timeout
timed out / timeout
remote end closed connection
connection reset
temporarily unavailable
```

If the normal 0.1-degree ID query exhausts its retries with a transient failure, Parcel100 splits the cell envelope at its longitude and latitude midpoints into four internal quarter envelopes.

Each quarter is queried separately using the same ID-only semantics. Returned IDs are merged into a Python set and sorted, which removes duplicates where a parcel intersects more than one quarter.

The fallback changes only ID discovery. The external output remains the normal single GeoJSON file for the original 0.1-degree cell.

A persistent error in a fallback quarter still stops the build rather than being misreported as an empty cell.

## Feature retrieval

For populated cells, Parcel100 uses the returned object IDs and requests features in batches.

Batch size is derived from the layer's reported `maxRecordCount`, capped at 2,000 records per request:

```text
batch_size = max(1, min(maxRecordCount, 2000))
```

The feature request includes:

```text
objectIds=<batch ids>
outFields=<only user-selected fields>
returnGeometry=true
outSR=4326
returnZ=false
returnM=false
geometryPrecision=<GUI precision>
```

This means unnecessary source attributes are never requested in the heavy feature-download pass.

Feature download requests use the same three-attempt retry mechanism. Batch size is not currently reduced adaptively after repeated failures.

## Output CRS

Parcel100 requests the server to return geometry in:

```text
EPSG:4326 / WGS 84
```

This avoids the manual reprojection step that was required during early QGIS testing and produces GeoJSON coordinates suitable for ArcGIS Earth.

The Florida source service used during development is not stored in WGS 84, but ArcGIS FeatureServer performs the requested `outSR=4326` transformation.

## Esri polygon geometry conversion

ArcGIS REST polygon geometry is returned as `rings`.

Parcel100 converts those rings into valid GeoJSON `Polygon` or `MultiPolygon` geometry.

The conversion does not rely solely on ring winding direction. Instead it:

1. closes rings when necessary;
2. drops zero-area/invalid-short rings;
3. calculates absolute ring area;
4. determines containment relationships between rings;
5. builds a containment-depth tree;
6. treats even-depth rings as polygon shells and direct odd-depth children as holes;
7. emits `Polygon` for one shell group or `MultiPolygon` for multiple groups.

This is intended to handle ordinary parcel geometry from services that do not preserve Esri winding rules consistently.

## Cell-boundary duplication

The spatial relationship is `intersects`, not a clipping operation.

If a parcel intersects two adjacent Master 4 cells, the complete parcel can appear in both output files.

This is intentional. A single cell remains independently useful and does not contain a chopped parcel at the boundary.

The tradeoff is some duplicated storage along cell edges.

## GeoJSON structure

Each file is written as a compact JSON `FeatureCollection` containing:

```text
type
name
bbox
master4
cell
source
features
```

Each feature contains:

```text
type = Feature
properties = selected source attributes
geometry = Polygon or MultiPolygon
```

JSON is written without decorative whitespace to reduce file size.

## Current file-write behavior

The current code writes directly to the final deterministic `.geojson` path.

It does **not** currently use a temporary file plus atomic rename. Because resume trusts an existing expected filename, a future hardening option is to validate existing JSON or use temporary-file/rename semantics before considering a cell complete.

Do not describe current v1.4 output as an atomic file write unless that implementation changes.

## Coordinate precision

GUI range:

```text
5 through 12
```

Default:

```text
7
```

The value is sent to the FeatureServer as `geometryPrecision`.

Higher precision increases coordinate text length and therefore GeoJSON size. The best value depends on the source geometry and intended use.

## Florida Recommended fields

Current preferred Florida fields are:

```text
OWN_NAME
PHY_ADDR1
PHY_CITY
PHY_ZIPCD
PARCEL_ID
ACRES
```

Matching is case-insensitive. The Florida service currently exposes the actual field as `Acres`; Parcel100 selects it through the uppercase preference while preserving the actual source field name in the output.

The preference list is not a schema requirement. Other services are discovered dynamically and the operator remains in control of the final selected fields.

## Threading

Metadata reads and builds run in a worker thread so the Tk GUI remains responsive enough to update progress/status while network requests are active.

The 100 cells are processed sequentially. The program intentionally does not fire 100 simultaneous requests at a public GIS service.

## Output performance rationale

GeoJSON is a text-based feature collection, not an indexed tile store. Very large exports can be expensive for viewers to parse and hold as vector objects.

The 100-cell architecture was selected after field testing larger exports. A roughly half-grid test produced a GeoJSON around 329 MB, while individual 0.1-degree production cells commonly landed in the low-MB to tens-of-MB range depending on parcel density.

The cell design therefore serves both:

- server-side query manageability;
- viewer-side memory/load manageability.

## Florida development services

Preferred current production source:

```text
https://services5.arcgis.com/GcvM6vDlR2gM4x31/arcgis/rest/services/FL_Parcels/FeatureServer/0
```

The Florida Statewide Cadastral service on services9 was also tested as an official-source comparison. It repeatedly exhibited slow responses, 504 Gateway Timeout errors and other transient failures. That testing is what drove the retry/fallback hardening.

## Real-world validation record

Owner-reported production runs include:

```text
Master 4: 82w,81w,30n,31n
55 populated files
45 empty cells skipped
663,277 parcel records written
```

Parcel100 1.4 reproduced this run with the new Acres field visible in ArcGIS Earth.

```text
Master 4: 82w,81w,29n,30n
92 populated files
8 empty cells skipped
547,183 parcel records written
about 314 MB total
```

```text
Grid 3: 83w,82w,30n,31n
63 populated files
37 empty cells skipped
78,837 parcel records
about two minutes for the full 100-cell pass
```

```text
Grid 4
99 populated files
1 empty cell
469,146 parcel records
```

```text
services9 cell 022
four-part ID fallback recovered 11,969 parcel IDs
```

Multiple output cells were opened together in ArcGIS Earth and parcel features were visually confirmed to draw, align geographically, and expose selected attributes in the feature popup.

These observations are field results, not universal performance guarantees.

## Current limitations

- Polygon FeatureServer layers only.
- Public/reachable services only; no login/token workflow.
- No automatic parcel-service discovery by state/county name.
- No clipping of parcels to cell boundaries.
- No deduplication across neighboring cell files.
- No automatic loading/unloading of cells inside ArcGIS Earth.
- No national parcel data is bundled with the program.
- Resume trusts an existing expected filename as complete.
- Feature batch size does not currently shrink after repeated download failures.
- Source quality, update schedule, allowed uses and field semantics remain the responsibility of the source provider/operator.

## Preservation rule

The program's core production behavior should remain deterministic:

```text
one Master 4 input
-> same 100 cell addresses
-> same output naming
-> completed filenames skipped
-> only populated unfinished cells written
```

Changes that alter cell numbering, naming, resume semantics, or output geometry should be treated as compatibility changes and tested against the Master 4 system before release.
